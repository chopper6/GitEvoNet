# master process, and functions used only by master

import math, os, pickle, multiprocessing as mp, networkx as nx
from operator import attrgetter
from time import process_time as ptime
from random import SystemRandom as sysRand
import output, plot_nets, minion, fitness
from time import sleep

# TODO: check Net class scope, is it suffic to just have in master?
# maybe rename to reduce confusion
class Net:
    def __init__(self, net, id):
        self.fitness = 0    #aim to max
        self.fitness_parts = [0]*3   #leaf-fitness, hub-fitness
        self.net = net.copy()
        assert(self.net != net)
        self.id = id  #irrelv i think

    def copy(self):
        copy = Net(self.net, self.id)
        copy.fitness = self.fitness
        copy.fitness_parts = self.fitness_parts
        assert (copy != self)
        return copy


def evolve_master(configs):
    # get configs
    num_workers = int(configs['number_of_workers'])
    output_dir = configs['output_directory'].replace("v4nu_minknap_1X_both_reverse/",'')  # no idea where this is coming from
    fitness_type = int(configs['fitness_type'])
    survive_percent = int(configs['percent_survive'])
    survive_fraction = float(survive_percent) / 100
    output_freq = float(configs['output_frequency'])
    max_iters = float(configs['max_iterations'])

    init_type = int(configs['initial_net_type'])
    start_size = int(configs['starting_size'])
    end_size = int(configs['ending_size'])
    worker_pop_size = int(configs['worker_population_size'])
    worker_gens = int(configs['worker_generations'])

    pop_size = worker_pop_size * num_workers
    num_survive = int(survive_fraction*pop_size)

    init_dirs(num_workers, output_dir)
    output.init_csv(output_dir, configs)

    #worker_pop_size, pop_size, num_survive, worker_gens = curr_gen_params(start_size+1, start_size, end_size, num_workers,survive_fraction)
    #print("Master init worker popn size: " + str(worker_pop_size) + ",\t num survive: " + str(num_survive))
    population = gen_init_population(init_type, start_size, pop_size)
    fitness.eval_fitness(population, fitness_type)

    size = start_size
    size_iters = 0
    while (size < end_size and size_iters < max_iters):

        if (size_iters % int(1 / output_freq) == 0):
            output.to_csv(population, output_dir)
            print("Master at gen " + str(size_iters) + ", with net size = " + str(size))

        #worker_pop_size, pop_size, num_survive, worker_gens = curr_gen_params(size, start_size, end_size, num_workers, survive_fraction)
        #print("At master gen: " + str(size_iters) + ",\t size " + str(size) + "=" + str(len(population[0].net.nodes())) + ",\tnets per worker = " + str(worker_pop_size) + ",\tpopn size = " + str(pop_size) + ",\tnum survive = " + str(num_survive) + ",\tworker gens = " + str(worker_gens))
        # DEBUG STUFF
        distrib, minions, readd = 0, 0, 0
        '''
        print ("Master population fitness: ")
        for p in range(len(population)):
            print(population[p].fitness)
        '''
        # check that population is unique
        '''
        for p in range(len(population)):
            for q in range(0, p):
                if (p != q): assert (population[p] != population[q])
        '''
        t0 = ptime()
        pool = mp.Pool(processes=num_workers)

        # DISTRIBUTE WORKERS
        for w in range(num_workers):
            dump_file =  output_dir + "workers/" + str(w) + "/arg_dump"
            seed = population[w % num_survive].copy()
            #randSeeds = [os.urandom(10000000) for i in range(worker_gens*worker_pop_size)] #diff seed for each mutation call
            randSeeds = os.urandom(sysRand().randint(0,1000000))
            assert(seed != population[w % num_survive])
            worker_args = [w, seed, worker_gens, worker_pop_size, min(worker_pop_size,num_survive), randSeeds, configs]
            with open(dump_file, 'wb') as file:
                pickle.dump(worker_args, file)
            pool.map_async(minion.evolve_minion, (dump_file,))
            sleep(.0001)

        t1 = ptime()
        distrib += t1 - t0

        pool.close()
        pool.join()
        pool.terminate()
        del population

        t0 = ptime()
        population = parse_worker_popn(num_workers, output_dir, num_survive)
        t1 = ptime()
        readd += t1 - t0

        size = len(population[0].net.nodes())
        size_iters += 1

        # Timing output
        '''
        print("distrib workers took " + str(distrib) + " secs.")
        print("minions took " + str(minions) + " secs.")
        print("reading in workers took " + str(readd) + " secs.\n")
        '''
    output.to_csv(population, output_dir)

    print("Evolution finished, generating images.")
    plot_nets.single_run_plots(output_dir)

    print("Master finished.")


def gen_init_population(init_type, start_size, pop_size):

    if (init_type == 0):
        population = [Net(nx.DiGraph(), i) for i in range(pop_size)] #change to generate, based on start_size

    elif (init_type == 1):
        population = [Net(nx.erdos_renyi_graph(start_size,.01, directed=True, seed=None), i) for i in range(pop_size)]
        # edge probability as param?

    else:
        print("ERROR in master.gen_init_population(): unknown init_type.")
        return

    #add sign to edges
    for p in range(pop_size):
        edge_list = population[p].net.edges()
        for edge in edge_list:
            sign = sysRand().randint(0, 1)
            if (sign == 0):     sign = -1
            population[p].net[edge[0]][edge[1]]['sign'] = sign

    return population


def init_dirs(num_workers, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for w in range(num_workers):
        dirr = output_dir + "workers/" + str(w)
        if not os.path.exists(dirr):  # move this to a single call during init
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


def curr_gen_params(size, start_size, end_size, num_workers, survive_fraction):
    #TODO: add island switch in CONFIGS for expon popn size curve

    percent_size = float(size) / float(end_size - start_size)
    const = 10
    worker_pop_size = 1
    worker_gens = math.ceil(-1*const*math.pow(percent_size,2)+const)
    # ISLAND # math.ceil(10 * math.pow(math.e, -4 * percent_size))
    pop_size = worker_pop_size * num_workers
    num_survive = int(pop_size * survive_fraction)
    if (num_survive < 1):
        num_survive = 1
        print("WARNING evo_master(): num_survive goes below 1, set to 1 instead.")
    #worker_gens = worker_pop_size

    return worker_pop_size, pop_size, num_survive, worker_gens



def evolve_master_sequential_debug(configs):
    # get configs
    num_workers = int(configs['number_of_workers'])
    output_dir = configs['output_directory'].replace("v4nu_minknap_1X_both_reverse/",'')  # no idea where this is coming from
    fitness_type = int(configs['fitness_type'])
    survive_percent = int(configs['percent_survive'])
    survive_fraction = float(survive_percent) / 100
    output_freq = float(configs['output_frequency'])

    # new configs
    init_type = int(configs['initial_net_type'])
    start_size = int(configs['starting_size'])
    end_size = int(configs['ending_size'])

    init_dirs(num_workers, output_dir)
    output.init_csv(output_dir, configs)

    worker_pop_size, pop_size, num_survive, worker_gens = curr_gen_params(start_size, start_size, end_size, num_workers,survive_fraction)
    print("Master init worker popn size: " + str(worker_pop_size) + ",\t num survive: " + str(num_survive))
    population = gen_init_population(init_type, start_size, pop_size)
    fitness.eval_fitness(population, fitness_type)

    size = start_size
    size_iters = 0
    while (size < end_size):

        if (size_iters % int(1 / output_freq) == 0):
            output.to_csv(population, output_dir)

        worker_pop_size, pop_size, num_survive, worker_gens = curr_gen_params(size+1, start_size, end_size, num_workers, survive_fraction)
        print("At size " + str(size) + "=" + str(len(population[0].net.nodes())) + ",\tnets per worker = " + str(worker_pop_size) + ",\tpopn size = " + str(pop_size) + ",\tnum survive = " + str(num_survive) + ",\tworker gens = " + str(worker_gens))
        # DEBUG STUFF
        distrib, minions, readd = 0, 0, 0
        '''
        print ("Master population fitness: ")
        for p in range(len(population)):
            print(population[p].fitness)
        '''
        # check that population is unique
        for p in range(len(population)):
            for q in range(0, p):
                if (p != q): assert (population[p] != population[q])

        t0 = ptime()
        pool = mp.Pool(processes=num_workers)

        # INSTEAD USES 1 SEQUENTIAL MINION
        for w in range(1):
            dump_file =  output_dir + "workers/" + str(w) + "/arg_dump"
            seed = population[w % num_survive].copy()
            assert(seed != population[w % num_survive])
            #randSeeds = [os.urandom(10000000) for i in range(worker_gens*worker_pop_size)] #diff seed for each mutation call
            randSeeds = os.urandom(sysRand().randint(0,1000000))
            worker_args = [w, seed, worker_gens, worker_pop_size, min(worker_pop_size,num_survive), randSeeds, configs]
            with open(dump_file, 'wb') as file:
                pickle.dump(worker_args, file)
            minion.evolve_minion(dump_file)

        t1 = ptime()
        distrib += t1 - t0

        pool.close()
        pool.join()
        pool.terminate()
        del population

        t0 = ptime()
        population = parse_worker_popn(num_workers, output_dir, num_survive)
        t1 = ptime()
        readd += t1 - t0

        size = len(population[0].net.nodes())
        size_iters += 1

        # Timing output
        '''
        print("distrib workers took " + str(distrib) + " secs.")
        print("minions took " + str(minions) + " secs.")
        print("reading in workers took " + str(readd) + " secs.\n")
        '''
    output.to_csv(population, output_dir)

    print("Evolution finished, generating images.")
    plot_nets.single_run_plots(output_dir)

    print("Master finished.")



