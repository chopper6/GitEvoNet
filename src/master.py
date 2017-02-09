# master process, and functions used only by master

import math, os, pickle
import multiprocessing as mp
from operator import attrgetter
from random import SystemRandom as sysRand
from time import sleep
import networkx as nx
import fitness, minion, output, plot_nets, net_generator, perturb, pressurize, draw_nets
import init


def evolve_master(configs):
    protocol = configs['protocol']
    if (protocol == 'scramble'):
        scramble_and_evolve(configs)
    elif (protocol == 'from seed'):
        evolve_from_seed(configs)
    elif (protocol == 'control'):
        control(configs)
    else:
        print("ERROR in master(): unknown protocol " + str(protocol))


def control(configs):
    output_dir = configs['output_directory'].replace("v4nu_minknap_1X_both_reverse/",'')  # no idea where this is coming from
    init_type = int(configs['initial_net_type'])
    start_size = int(configs['starting_size'])
    fitness_type = int(configs['fitness_type'])

    pop_size = 1

    population = net_generator.init_population(init_type, start_size, pop_size)
    print("Control individual generated, applying pressure.")

    pressure_results = pressurize.pressurize(configs, population[0].net)
    population[0].fitness_parts[0], population[0].fitness_parts[1], population[0].fitness_parts[2] = pressure_results[0], pressure_results[1],pressure_results[2]
    population = fitness.eval_fitness(population)
    output.to_csv(population, output_dir)

    print("Control run finished.")

def scramble_and_evolve(configs):
    #curr just scramble edges, same num
    #TODO: merge with evolve_from_seed more elegantly

    #CONFIGS
    num_workers = int(configs['number_of_workers'])
    output_dir = configs['output_directory'].replace("v4nu_minknap_1X_both_reverse/",'')  # no idea where this is coming from
    survive_percent = float(configs['percent_survive'])
    survive_fraction = float(survive_percent) / 100
    output_freq = float(configs['output_frequency'])
    max_iters = float(configs['max_iterations'])
    percent_perturb = float(configs['percent_perturb'])/100

    pop_size = num_workers
    worker_gens = worker_pop_size = 1
    num_survive = math.ceil(survive_fraction*pop_size)

    init_dirs(num_workers, output_dir)
    output.init_csv(output_dir, configs)

    #init, pre scramble
    vinayagam = net_generator.Net(init.load_network(configs),0)
    init_size = (len(vinayagam.net.edges()))
    pressure_results = pressurize.pressurize(configs, vinayagam.net)
    vinayagam.fitness_parts[0], vinayagam.fitness_parts[1], vinayagam.fitness_parts[2] = pressure_results[0], pressure_results[1], pressure_results[2]
    fitness.eval_fitness([vinayagam])
    output.to_csv([vinayagam], output_dir)
    
    #scramble
    perturb.scramble_edges(vinayagam.net, percent_perturb)
    pressure_results = pressurize.pressurize(configs, vinayagam.net)

    population = []
    for p in range(pop_size):
        population.append(vinayagam.copy())
        population[p].fitness_parts[0], population[p].fitness_parts[1], population[p].fitness_parts[2] = pressure_results[0],  pressure_results[1],  pressure_results[2]
    fitness.eval_fitness(population)
    #output.to_csv([vinayagam], output_dir)
    assert (init_size == len(population[0].net.edges()))
    print("Finished scrambling, beginning the return evolution.")


    size_iters = 0
    while (size_iters < max_iters):

        if (size_iters % int(1 / output_freq) == 0):
            output.to_csv(population, output_dir)
            print("Master at gen " + str(size_iters) + ", with net node size = " + str(len(population[0].net.nodes())) + ", and net edge size of " + str(len(population[0].net.edges())) + ",\t " + str(num_survive) + " survive out of " + str(pop_size) + ", with " + str(worker_pop_size) + " nets per worker.")

        #debug(population) 
        pool = mp.Pool(processes=num_workers)

        # distribute workers
        for w in range(num_workers):
            dump_file =  output_dir + "workers/" + str(w) + "/arg_dump"
            seed = population[w % num_survive].copy()
            randSeeds = os.urandom(sysRand().randint(0,1000000))
            assert(seed != population[w % num_survive])
            worker_args = [w, seed, worker_gens, worker_pop_size, min(worker_pop_size,num_survive), randSeeds, configs]
            with open(dump_file, 'wb') as file:
                pickle.dump(worker_args, file)
            pool.map_async(minion.evolve_minion, (dump_file,))
            sleep(.0001)

        pool.close()
        pool.join()
        pool.terminate()

        del population
        population = parse_worker_popn(num_workers, output_dir, num_survive)

        size_iters += 1

    output.to_csv(population, output_dir)

    print("Evolution finished, generating images.")
    plot_nets.single_run_plots(output_dir)
    print("Master finished.")


def evolve_from_seed(configs):
    # get configs
    num_workers = int(configs['number_of_workers'])
    output_dir = configs['output_directory'].replace("v4nu_minknap_1X_both_reverse/",'')  # no idea where this is coming from
    survive_percent = float(configs['percent_survive'])
    survive_fraction = float(survive_percent) / 100
    output_freq = float(configs['output_frequency'])
    draw_freq =  float(configs['draw_frequency'])
    max_iters = float(configs['max_iterations'])

    worker_survive_fraction = float(configs['worker_percent_survive'])/100

    init_type = int(configs['initial_net_type'])
    start_size = int(configs['starting_size'])
    end_size = int(configs['ending_size'])

    init_dirs(num_workers, output_dir)
    output.init_csv(output_dir, configs)
    draw_nets.init(output_dir)

    worker_pop_size, pop_size, num_survive, worker_gens = curr_gen_params(start_size, end_size, num_workers,survive_fraction, 10000000)
    print("Master init worker popn size: " + str(worker_pop_size) + ",\t num survive: " + str(num_survive) + " out of total popn of " + str(pop_size))

    population = net_generator.init_population(init_type, start_size, pop_size)
    fitness.eval_fitness(population)
    output.deg_change_csv(population, output_dir)

    total_gens = 0
    size = start_size
    size_iters = 0
    while (size < end_size and size_iters < max_iters):

        worker_pop_size, pop_size, num_survive, worker_gens = curr_gen_params(size, end_size, num_workers, survive_fraction, num_survive)

        if (size_iters % int(1 / output_freq) == 0):
            output.to_csv(population, output_dir, total_gens)
            print("Master at gen " + str(size_iters) + ", with net size = " + str(size) + ", " + str(num_survive) + "<=" + str(len(population)) + " survive out of " + str(pop_size))
            worker_percent_survive = math.ceil(worker_survive_fraction * worker_pop_size)
            print("Workers: over " + str(worker_gens) + " gens " + str(worker_percent_survive) + " nets survive out of " + str(worker_pop_size) + ".")

        if (size_iters % int(1 / draw_freq) == 0):
            draw_nets.basic(population, output_dir, total_gens)


        #debug(population)
        pool = mp.Pool(processes=num_workers)

        # distribute workers
        for w in range(num_workers):
            dump_file =  output_dir + "workers/" + str(w) + "/arg_dump"
            seed = population[w % num_survive].copy()
            randSeeds = os.urandom(sysRand().randint(0,1000000))
            assert(seed != population[w % num_survive])
            worker_args = [w, seed, worker_gens, worker_pop_size, min(worker_pop_size,num_survive), randSeeds, configs]
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
        size_iters += 1
        total_gens += worker_gens

    output.to_csv(population, output_dir)
    output.deg_change_csv(population, output_dir)
    draw_nets.basic(population, output_dir, total_gens)

    print("Evolution finished, generating images.")
    plot_nets.single_run_plots(output_dir)
    print("Master finished.")


def init_dirs(num_workers, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
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
