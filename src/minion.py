# worker processes

import math, pickle, random, os, time
import output, fitness, pressurize, mutate, init, util
from time import process_time as ptime

def work(configs, rank):
    output_dir = configs['output_directory']
    max_gen = int(configs['max_generations'])
    gen = 0

    print ("\t\t\t\tworker #"+str(rank)+" is working,\t")
    progress = output_dir + "/progress.txt"

    #init, see if cont run
    t_start = time.time()
    while not os.path.isfile(progress):  # master will create this file
        time.sleep(2)

    while not (os.path.getmtime(progress) + .5 < time.time()):  # check that file has not been recently touched
        time.sleep(.5)

    if (True): #lol just to avoid re-indenting in vi
        with open(progress, 'r') as file:
            line = file.readline()
            if (line == 'Done' or line == 'Done\n'):
                if (rank == 1 or rank==32 or rank==63): util.cluster_print(output_dir,"Worker #" + str(rank) + " + exiting.")
                return  # no more work to be done
            else:
                gen = int(line.strip())
                #util.cluster_print(output_dir,"Worker #" + str(rank) + " got gen " + str(gen) + " from progress file.")

    t_end = time.time()
    if ((rank == 1 or rank == 32 or rank == 63 or rank == 128) and gen % 100 == 0): util.cluster_print(output_dir,"worker #" + str(rank) + " finished init in " + str(t_end-t_start) + " seconds.")

    estim_time = 4
    while gen < max_gen:
        t_start = time.time()

        worker_file = str(output_dir) + "/to_workers/" + str(gen) + "/" + str(rank)
        #util.cluster_print(output_dir,"worker #" + str(rank) + " looking for file: " + str(worker_file))
        i=1
        num_estim = 0
        while not os.path.isfile(worker_file):
            if (num_estim < 4):
                time.sleep(estim_time/4)
                num_estim += 1
            else: 
                time.sleep(4)
                estim_time += 4
            i+=1

        while not (os.path.getmtime(worker_file) + .4 < time.time()):
            time.sleep(.5)

        t_end = time.time()
        t_elapsed = t_end - t_start
        if ((rank == 1 or rank==32 or rank==63 or rank==128)): util.cluster_print(output_dir,"Worker #" + str(rank) + " starting evolution after waiting " + str(t_elapsed) + " seconds and checking dir " + str(i) + " times. Starts at gen " + str(gen))
        evolve_minion(worker_file, gen, rank, output_dir)
        gen+=1


def evolve_minion(worker_file, gen, rank, output_dir):
    t_start = time.time()

    with open(str(worker_file), 'rb') as file:
        worker_ID, seed, worker_gens, pop_size, num_return, randSeed, curr_gen, configs = pickle.load(file)
        file.close()

    survive_fraction = float(configs['worker_percent_survive'])/100
    num_survive = math.ceil(survive_fraction * pop_size)
    output_dir = configs['output_directory'].replace("v4nu_minknap_1X_both_reverse/", '')
    #output_dir += str(worker_ID)
    max_gen = int(configs['max_generations'])
    control = configs['control']
    if (control == "None"): control = None
    fitness_direction = str(configs['fitness_direction'])

    node_edge_ratio = float(configs['edge_to_node_ratio'])

    random.seed(randSeed)
    population = gen_population_from_seed(seed, pop_size)
    start_size = len(seed.net.nodes())
    pressurize_time = 0
    mutate_time = 0
    
    for g in range(worker_gens):
        gen_percent = float(curr_gen/max_gen)
        if (g != 0):
            for p in range(num_survive,pop_size):
                population[p] = population[p%num_survive].copy()
                #assert (population[p] != population[p%num_survive])
                #assert (population[p].net != population[p % num_survive].net)

        for p in range(pop_size):
            t0 = ptime()
            mutate.mutate(configs, population[p].net, gen_percent, node_edge_ratio)
            t1 = ptime()
            mutate_time += t1-t0

            if (control == None):
                pressure_results = pressurize.pressurize(configs, population[p].net, None)  # false: don't track node fitness, None: don't write instances to file
                population[p].fitness_parts[0], population[p].fitness_parts[1], population[p].fitness_parts[2] = pressure_results[0], pressure_results[1], pressure_results[2]

            else: util.cluster_print(output_dir,"ERROR in minion(): unknown control config: " + str(control))

        old_popn = population
        population = fitness.eval_fitness(old_popn, fitness_direction)
        del old_popn
        #debug(population,worker_ID, output_dir)
        curr_gen += 1
    write_out_worker(output_dir + "/to_master/" + str(gen) + "/" + str(rank), population, num_return)
    
    # some output, probably outdated
    if (worker_ID == 0):
        orig_dir = configs['output_directory']
        end_size = len(population[0].net.nodes())
        growth = end_size - start_size
        output.minion_csv(orig_dir, pressurize_time, growth, end_size)
        #debug(population, worker_ID, output_dir)
        #if (worker_ID==0): util.cluster_print(output_dir,"Pressurizing took " + str(pressurize_time) + " secs, while mutate took " + str(mutate_time) + " secs.")

    t_end = time.time()
    time_elapsed = t_end - t_start
    if (rank == 1 or rank==32 or rank==63): util.cluster_print(output_dir,"Worker #" + str(rank) + " finishing after " + str(time_elapsed) + " seconds")


def write_out_worker(worker_file, population, num_return):
    # overwrite own input file with return population
    #util.cluster_print(output_dir,"worker writing out to " + str(worker_file) + "\n")
    with open(worker_file, 'wb') as file:
        pickle.dump(population[:num_return], file)
        file.close()

def gen_population_from_seed(seed, num_survive):
    population = []
    for p in range(num_survive):
        population.append(seed.copy())
        assert(population[-1] != seed)
    return population

def debug(population, worker_ID, output_dir):
    pop_size = len(population)
    if (worker_ID == 0):
        print ("Minion population fitness: ")
        for p in range(pop_size):
            util.cluster_util.cluster_print(output_dir,population[p].fitness_parts[2])
    # check that population is unique
    for p in range(pop_size):
        for q in range(0, p):
            if (p != q): assert (population[p] != population[q])

    util.cluster_print(output_dir,"Minion nets exist?")
    for p in range(pop_size):
            util.cluster_print(output_dir,population[p].net)

