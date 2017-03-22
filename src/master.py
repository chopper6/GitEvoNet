# master process, and functions used only by master

import math, os, pickle
import multiprocessing as mp
from operator import attrgetter
from random import SystemRandom as sysRand
from time import sleep
import networkx as nx
import fitness, minion, output, plot_nets, net_generator, perturb, pressurize, draw_nets, plot_fitness, node_fitness
import init


def evolve_master(configs):
    protocol = configs['protocol']
    if (protocol == 'from seed'):
        evolve_from_seed(configs)
    else:
        print("ERROR in master(): unknown protocol " + str(protocol))

def evolve_from_seed(configs):
    # get configs
    num_workers = int(configs['number_of_workers'])
    output_dir = configs['output_directory']
    survive_percent = float(configs['percent_survive'])
    survive_fraction = float(survive_percent) / 100
    num_output = float(configs['num_output'])
    num_draw =  float(configs['num_drawings'])
    max_gen = float(configs['max_generations'])

    worker_survive_fraction = float(configs['worker_percent_survive'])/100
    init_type = str(configs['initial_net_type'])
    start_size = int(configs['starting_size'])
    end_size = int(configs['ending_size'])

    instance_file = configs['instance_file']

    draw_layout = str(configs['draw_layout'])
    num_fitness_plots = int(configs['num_fitness_plots']) #ASSUMES != 0
    if (num_fitness_plots > max_gen or num_output > max_gen or num_draw > max_gen):
        print("WARNING master(): more output requested than generations.")

    init_dirs(num_workers, output_dir)
    output.init_csv(output_dir, configs)
    draw_nets.init(output_dir)

    worker_pop_size, pop_size, num_survive, worker_gens = curr_gen_params(start_size, end_size, num_workers,survive_fraction, 10000000)
    print("Master init worker popn size: " + str(worker_pop_size) + ",\t num survive: " + str(num_survive) + " out of total popn of " + str(pop_size))

    population = net_generator.init_population(init_type, start_size, pop_size, configs)

    #init fitness, uses net0 since effectively a random choice (may disadv init, but saves lotto time)
    #TODO: for final results, should NOT just use net0
    #instead pass to workers, but w/o any mutation and just for a single gen

    pressure_results = pressurize.pressurize(configs, population[0].net, True, instance_file+"Xiter0.csv") #True: track node fitness
    population[0].fitness_parts[0], population[0].fitness_parts[1], population[0].fitness_parts[2] = pressure_results[0], pressure_results[1], pressure_results[2]
    fitness.eval_fitness([population[0]])
    output.deg_change_csv([population[0]], output_dir)

    total_gens = 0
    size = start_size
    iter = 0
    while (size < end_size and total_gens < max_gen):

        worker_pop_size, pop_size, num_survive, worker_gens = curr_gen_params(size, end_size, num_workers, survive_fraction, num_survive)

        if (iter % int(max_gen / num_output) == 0):
            output.to_csv(population, output_dir, total_gens)
            print("Master at gen " + str(total_gens) + ", with net size = " + str(size) + ", " + str(num_survive) + "<=" + str(len(population)) + " survive out of " + str(pop_size))
            worker_percent_survive = math.ceil(worker_survive_fraction * worker_pop_size)
            print("Workers: over " + str(worker_gens) + " gens " + str(worker_percent_survive) + " nets survive out of " + str(worker_pop_size) + ".\n")

            nx.write_edgelist(population[0].net, output_dir+"/fittest_net.edgelist")

        if (iter % int(max_gen / num_draw) == 0 and num_draw != 0 ):
            draw_nets.basic(population, output_dir, total_gens, draw_layout)

        if (iter % int(max_gen/num_fitness_plots) ==0):
            #if first gen, have already pressurized w/net[0]
            if (iter != 0): pressure_results = pressurize.pressurize(configs, population[0].net, True, instance_file+"Xiter"+str(iter)+".csv" )  # True: track node fitness
            node_info = pressure_results[3]
            node_fitness.write_out(output_dir + "/node_info/" + str(iter) + ".csv", node_info)


        #debug(population)
        pool = mp.Pool(processes=num_workers)

        # distribute workers
        for w in range(num_workers):
            dump_file =  output_dir + "workers/" + str(w) + "/arg_dump"
            seed = population[w % num_survive].copy()
            randSeeds = os.urandom(sysRand().randint(0,1000000))
            assert(seed != population[w % num_survive])
            worker_args = [w, seed, worker_gens, worker_pop_size, min(worker_pop_size,num_survive), randSeeds, total_gens, configs]
            with open(dump_file, 'wb') as file:
                pickle.dump(worker_args, file)
            pool.map_async(minion.evolve_minion, (dump_file,))
            #minion.evolve_minion(dump_file)
            sleep(.0001)

        pool.close()
        pool.join()
        pool.terminate()

        del population
        population = parse_worker_popn(num_workers, output_dir, num_survive)
        size = len(population[0].net.nodes())
        iter += 1
        total_gens += worker_gens

    #final outputs
    nx.write_edgelist(population[0].net, output_dir+"/fittest_net.edgelist")

    output.to_csv(population, output_dir, total_gens)
    output.deg_change_csv(population, output_dir)
    draw_nets.basic(population, output_dir, total_gens, draw_layout)

    if (iter != 0): pressure_results = pressurize.pressurize(configs, population[0].net, True, instance_file+"Xiter"+str(iter)+".csv")  # True: track node fitness
    node_info = pressure_results[3]
    node_fitness.write_out(output_dir + "/node_info/" + str(iter) + ".csv", node_info)
    plot_name = iter

    plot_fitness.all_fitness_plots(output_dir)


    print("Evolution finished, generating images.")
    plot_nets.single_run_plots(output_dir)
    print("Master finished.")


def init_dirs(num_workers, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(output_dir + "/node_info/"):
        os.makedirs(output_dir + "/node_info/")
    if not os.path.exists(output_dir + "/instances/"):
        os.makedirs(output_dir + "/instances/")
    for w in range(num_workers):
        dirr = output_dir + "workers/" + str(w)
        if not os.path.exists(dirr):
            os.makedirs(dirr)


def parse_worker_popn (num_workers, output_dir, num_survive):
    popn = []
    for w in range(num_workers):
        dump_file = output_dir + "workers/" + str(w) + "/arg_dump"
        with open(dump_file, 'rb') as file:
            worker_pop = pickle.load(file)
        for indiv in worker_pop:
            popn.append(indiv)
    sorted_popn = sorted(popn, key=attrgetter('fitness'), reverse=True)
    return sorted_popn[:num_survive]


def curr_gen_params(size, end_size, num_workers, survive_fraction, prev_num_survive):


    worker_pop_size = math.floor(end_size/size)

    worker_gens = worker_pop_size
    # ISLAND #
    # percent_size = float(size) / float(end_size)
    # math.ceil(10 * math.pow(math.e, -4 * percent_size))
    pop_size = worker_pop_size * num_workers
    num_survive = int(pop_size * survive_fraction)
    if (num_survive < 1):  num_survive = 1
    if (num_survive > prev_num_survive):   num_survive = prev_num_survive


    return worker_pop_size, pop_size, num_survive, worker_gens


def debug(population):
    '''
    print("Master population fitness: ")
    for p in range(len(population)):
        print(population[p].fitness)
    '''
    # check that population is unique
    for p in range(len(population)):
        for q in range(0, p):
            if (p != q): assert (population[p] != population[q])

