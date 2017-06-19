# master process, and functions used only by master

import math, os, pickle, sys, time, shutil
#os.environ['analysis'] = "/home/2014/choppe1/Documents/EvoNet/virt_workspace/lib/analysis"
#sys.path.insert(0, os.getenv('analysis'))
import multiprocessing as mp
from random import SystemRandom as sysRand
from time import sleep
import networkx as nx
import fitness, minion, output, plot_nets, net_generator, perturb, pressurize, draw_nets, plot_fitness, node_fitness, mutate

def evolve_master(batch_dir, configs, num_workers, cont):
    protocol = configs['protocol']
    if (protocol == 'from seed'):
        evolve_from_seed(batch_dir, configs, num_workers, cont)
    else:
        print("ERROR in master(): unknown protocol " + str(protocol))
    return

def evolve_from_seed(batch_dir, configs, num_workers, cont):
    # get configs
    #num_workers = int(configs['number_of_workers'])
    output_dir = configs['output_directory']
    survive_percent = float(configs['percent_survive'])
    survive_fraction = float(survive_percent) / 100
    num_output = int(configs['num_output'])
    num_net_output = int(configs['num_net_output'])
    num_draw =  int(configs['num_drawings'])
    max_gen = int(configs['max_generations'])
    debug = (configs['debug'])
    if (debug == 'True'): debug = True
    worker_pop_size_config = int(configs['num_worker_nets'])
    worker_survive_fraction = float(configs['worker_percent_survive'])/100
    init_type = str(configs['initial_net_type'])
    start_size = int(configs['starting_size'])
    end_size = int(configs['ending_size'])
    #instance_file = configs['instance_file']
    num_grow = int(configs['num_grows'])
    edge_node_ratio = float(configs['edge_to_node_ratio'])

    num_instance_output = int(configs['num_instance_output'])
    instance_file = configs['instance_file']
    if (num_instance_output==0): instance_file = None

    size, total_gens, iter, population, num_survive = None, None, None, None, None #just to avoid annoying warnings

    if (cont == False):
        init_dirs(num_workers, output_dir, batch_dir)
        output.init_csv(output_dir, configs)
        #draw_nets.init(output_dir)

        worker_pop_size, pop_size, num_survive, worker_gens = curr_gen_params(start_size, end_size, num_workers,survive_fraction, -1, worker_pop_size_config)
        print("Master init worker popn size: " + str(worker_pop_size) + ",\t num survive: " + str(num_survive) + " out of total popn of " + str(pop_size))

        population = net_generator.init_population(init_type, start_size, pop_size, configs)
        #init fitness, uses net0 since effectively a random choice (may disadv init, but saves lotto time)
        pressure_results = pressurize.pressurize(configs, population[0].net, instance_file + "Xiter0.csv")  # false: don't track node fitness, None: don't write instances to file
        population[0].fitness_parts[0], population[0].fitness_parts[1], population[0].fitness_parts[2] = pressure_results[0], pressure_results[1], pressure_results[2]
        fitness.eval_fitness([population[0]])

        output.deg_change_csv([population[0]], output_dir)

        total_gens, size, iter = 0, start_size, 0

    elif (cont == True):
        #curr not able to use dynamic worker gens and parallel islands
        worker_pop_size, pop_size, num_survive, worker_gens = curr_gen_params(start_size, end_size, num_workers, survive_fraction, -1, worker_pop_size_config)
        with open(batch_dir + "/progress.txt", 'r') as file:
            lines = file.readlines()
            iter = lines[-1]
        population = parse_worker_popn(num_workers, iter, batch_dir, num_survive)
        size = len(population[0].net.nodes())
        total_gens = iter #also temp, assumes worker gens = 1

    else:
        print("ERROR in master(): unknown cont arg: " + str(cont))

    while (size <= end_size and total_gens < max_gen):
        worker_pop_size, pop_size, num_survive, worker_gens = curr_gen_params(size, end_size, num_workers, survive_fraction, num_survive, worker_pop_size_config)

        if (iter % int(max_gen / num_output) == 0):
            output.to_csv(population, output_dir, total_gens)
            print("Master at gen " + str(total_gens) + ", with net size = " + str(size) + " nodes and " + str(len(population[0].net.edges())) + " edges, " + str(num_survive) + "<=" + str(len(population)) + " survive out of " + str(pop_size))
            worker_percent_survive = worker_pop_size #should match however workers handle %survive
            print("Workers: over " + str(worker_gens) + " gens " + str(worker_percent_survive) + " nets survive out of " + str(worker_pop_size) + ".\n")

            nx.write_edgelist(population[0].net, output_dir+"/fittest_net.edgelist")

        if (num_instance_output != 0):
            if (iter % int(max_gen / num_instance_output) == 0):
                # if first gen, have already pressurized w/net[0]
                if (iter != 0): pressure_results = pressurize.pressurize(configs, population[0].net, instance_file + "Xiter" + str( iter) + ".csv")

        #if (iter % int(max_gen / num_draw) == 0 and num_draw != 0 ):
            #draw_nets.basic(population, output_dir, total_gens, draw_layout)

        if (iter % int(max_gen/num_net_output) ==0):
            nx.write_edgelist(population[0].net, output_dir + "/nets/" + str(iter))

        if (num_grow != 0): #WILL NOT WORK WELL WITH ISLAND ALGO, OR MULT WORKER GENS
            #ASSUMES GROWTH ONLY FOR 1st HALF
            rate = int(max_gen/(2*num_grow))
            if ((iter-start_size) % rate ==0 and iter < (max_gen/2 - start_size*rate)):
                for p in range(len(population)):
                    mutate.add_nodes(population[p].net, 1, edge_node_ratio)

        # MPI PARALLEL
        # progress file = dir, gen
        write_mpi_info(batch_dir, output_dir, iter)

        #debug(population)

        # distribute workers
        if (debug == True): #sequential debug
            dump_file = output_dir + "to_workers/" + str(iter) + "/0"
            seed = population[0].copy()
            randSeeds = os.urandom(sysRand().randint(0, 1000000))
            worker_args = [0, seed, worker_gens, worker_pop_size, min(worker_pop_size, num_survive), randSeeds,total_gens, configs]
            with open(dump_file, 'wb') as file:
                pickle.dump(worker_args, file)
            #pool.map_async(minion.evolve_minion, (dump_file,))
            minion.evolve_minion(dump_file)
            sleep(.0001)

        else:
            for w in range(1,num_workers+1):
                dump_file =  batch_dir + "/to_workers/" + str(iter) + "/" + str(w)
                #print("master dumping to file: " + str(dump_file))
                seed = population[w % num_survive].copy()
                randSeeds = os.urandom(sysRand().randint(0,1000000))
                assert(seed != population[w % num_survive])
                worker_args = [w, seed, worker_gens, worker_pop_size, min(worker_pop_size,num_survive), randSeeds, total_gens, configs]
                with open(dump_file, 'wb') as file:
                    pickle.dump(worker_args, file)


        del population
        if (debug == True):
            print("debug is ON") 
            num_workers, num_survive = 1,1


        watch(configs, iter, num_workers, batch_dir)
        population = parse_worker_popn(num_workers, iter, batch_dir, num_survive)
        size = len(population[0].net.nodes())
        iter += 1
        total_gens += worker_gens

    #workers don't need until next config run
    os.remove(batch_dir + "/progress.txt")

    #final outputs
    nx.write_edgelist(population[0].net, output_dir+"/nets/"+str(iter))

    output.to_csv(population, output_dir, total_gens)
    output.deg_change_csv(population, output_dir)
    #draw_nets.basic(population, output_dir, total_gens, draw_layout)

    print("Evolution finished, generating images.")
    plot_nets.single_run_plots(output_dir)
    #instances.analyze(output_dir)

    with open(batch_dir + "/finished_dirs.txt", 'a') as out:
        out.write(output_dir + "\n")

    print("Master finished.")
    return


def init_dirs(num_workers, output_dir, batch_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(output_dir + "/node_info/"):
        os.makedirs(output_dir + "/node_info/")
    if not os.path.exists(output_dir + "/instances/"):
        os.makedirs(output_dir + "/instances/")
    if not os.path.exists(output_dir + "/nets/"):
        os.makedirs(output_dir + "/nets/")
    if not os.path.exists(batch_dir + "/to_workers/"):
        os.makedirs(batch_dir + "/to_workers/")
    if not os.path.exists(batch_dir + "/to_master/"):
        os.makedirs(batch_dir + "/to_master/")


def parse_worker_popn (num_workers, iter, batch_dir, num_survive):
    popn = []
    for w in range(1,num_workers+1): #assumes master is rank0, hence workers are [1,#workers+1]
        dump_file = batch_dir + "/to_master/" + str(iter) + "/" + str(w)
        with open(dump_file, 'rb') as file:
            worker_pop = pickle.load(file)
        i=0
        for indiv in worker_pop:
            popn.append(indiv)
            i+=1

    #del old gen dirs
    shutil.rmtree(batch_dir + "/to_master/" + str(iter))
    shutil.rmtree(batch_dir + "/to_workers/" + str(iter))

    sorted_popn = fitness.eval_fitness(popn)
    return sorted_popn[:num_survive]


def curr_gen_params(size, end_size, num_workers, survive_fraction, prev_num_survive, worker_pop_size_config):

    worker_pop_size = math.floor(end_size/size)

    worker_gens = 1 #TODO: worker_pop_size
    # ISLAND #
    # percent_size = float(size) / float(end_size)
    # math.ceil(10 * math.pow(math.e, -4 * percent_size))

    pop_size = worker_pop_size_config * num_workers
    num_survive = int(pop_size * survive_fraction)
    if (num_survive < 1):  num_survive = 1
    if (prev_num_survive > 0):
        if (num_survive > prev_num_survive):   num_survive = prev_num_survive

    #TODO: temp manual pop size set
    return worker_pop_size_config, pop_size, num_survive, worker_gens


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



def watch(configs, iter, num_workers, batch_dir):

    dump_dir = batch_dir + "/to_master/" + str(iter)

    done, i = False, 1

    while not done:
        time.sleep(1.5*i)  #checks less and less freq
        i += 1
        #print(dump_dir)
        for root, dirs, files in os.walk(dump_dir): 
            #print(str(dump_dir) + " has " + str(len(files)) + " files in it.")
            if (len(files) == num_workers):
                for f in files:
                    if (os.path.getmtime(root + "/" + f) + 2 > time.time()): break #ie file may still be being written

                return


def write_mpi_info(batch_dir, output_dir, iter):

    if (iter ==0):
        with open(batch_dir + "/progress.txt", 'w') as out:
            out.write(output_dir + "\n")

    with open(batch_dir + "/progress.txt", 'a') as out:
        out.write(str(iter) + "\n")
    if not os.path.exists(batch_dir + "/to_workers/" + str(iter)):
        os.makedirs(batch_dir + "/to_workers/" + str(iter))
    if not os.path.exists(batch_dir + "/to_master/" + str(iter)):
        os.makedirs(batch_dir + "/to_master/" + str(iter))
    else: print("WARNING in master.write_mpi_info(): dir /to_master/" + str(iter) + " already exists...")
