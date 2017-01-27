# master process, and functions used only by master

import math, os, pickle
import multiprocessing as mp
from operator import attrgetter
from random import SystemRandom as sysRand
from time import sleep

import fitness, minion, output, plot_net, net_generator


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

    init_dirs(num_workers, output_dir)
    output.init_csv(output_dir, configs)

    worker_pop_size, pop_size, num_survive, worker_gens = curr_gen_params(start_size, end_size, num_workers,survive_fraction)
    print("Master init worker popn size: " + str(worker_pop_size) + ",\t num survive: " + str(num_survive))

    population = net_generator.init_population(init_type, start_size, pop_size)
    fitness.eval_fitness(population, fitness_type)

    size = start_size
    size_iters = 0
    while (size < end_size and size_iters < max_iters):

        worker_pop_size, pop_size, num_survive, worker_gens = curr_gen_params(size, end_size, num_workers, survive_fraction)

        if (size_iters % int(1 / output_freq) == 0):
            output.to_csv(population, output_dir)
            print("Master at gen " + str(size_iters) + ", with net size = " + str(size) + ", " + str(num_survive) + " survive out of " + str(pop_size) + ", with " + str(worker_pop_size) + " nets per worker.")

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
            minion.evolve_minion(dump_file)  #changed this line from map_async
            sleep(.0001)

        pool.close()
        pool.join()
        pool.terminate()

        del population
        population = parse_worker_popn(num_workers, output_dir, num_survive)

        size = len(population[0].net.nodes())
        size_iters += 1

    output.to_csv(population, output_dir)

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


def curr_gen_params(size, end_size, num_workers, survive_fraction):

    percent_size = float(size) / float(end_size)
    worker_pop_size = math.floor(end_size/size)
    worker_gens = worker_pop_size
    # ISLAND # math.ceil(10 * math.pow(math.e, -4 * percent_size))
    pop_size = worker_pop_size * num_workers
    num_survive = int(pop_size * survive_fraction)
    if (num_survive < 1):
        num_survive = 1
        print("WARNING evo_master(): num_survive goes below 1, set to 1 instead.")

    return worker_pop_size, pop_size, num_survive, worker_gens


def debug(population):
    print("Master population fitness: ")
    for p in range(len(population)):
        print(population[p].fitness)

    # check that population is unique
    for p in range(len(population)):
        for q in range(0, p):
            if (p != q): assert (population[p] != population[q])