# worker processes

import math, pickle
import output, fitness, pressurize
import mutate
from time import process_time as ptime
import random
import control_fitness

def evolve_minion(worker_file):
    with open(str(worker_file), 'rb') as file:
        worker_ID, seed, worker_gens, pop_size, num_return, randSeed, curr_gen, configs = pickle.load(file)
        file.close()

    survive_fraction = float(configs['worker_percent_survive'])/100
    num_survive = math.ceil(survive_fraction * pop_size)
    output_dir = configs['output_directory'].replace("v4nu_minknap_1X_both_reverse/", '')
    output_dir += str(worker_ID)
    max_gen = int(configs['max_generations'])
    control = configs['control']
    if (control == "None"): control = None

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
          
            t0 = ptime()
            if (control == None):
                population[p].fitness = pressurize.pressurize(configs, population[p].net, False, None) #false: don't track node fitness, None: don't write instances to file
                t1 = ptime()
                pressurize_time += t1-t0

        old_popn = population
        population = fitness.eval_fitness(old_popn)
        del old_popn
        #debug(population,worker_ID)
        curr_gen += 1
    write_out_worker(worker_file, population, num_return)
    
    # some output
    if (worker_ID == 0):
        orig_dir = configs['output_directory'] #.replace("v4nu_minknap_1X_both_reverse/", '')
        end_size = len(population[0].net.nodes())
        growth = end_size - start_size
        output.minion_csv(orig_dir, pressurize_time, growth, end_size)
        #debug(population, worker_ID)
        #if (worker_ID==0): print("Pressurizing took " + str(pressurize_time) + " secs, while mutate took " + str(mutate_time) + " secs.")

def write_out_worker(worker_file, population, num_return):
    # overwrite own input file with return population
    with open(worker_file, 'wb') as file:
        pickle.dump(population[:num_return], file)
        file.close()

def gen_population_from_seed(seed, num_survive):
    population = []
    for p in range(num_survive):
        population.append(seed.copy())
        assert(population[-1] != seed)
    return population

def debug(population, worker_ID):
    pop_size = len(population)
    if (worker_ID == 0):
        print ("Minion population fitness: ")
        for p in range(pop_size):
            print(population[p].fitness_parts[2])
    # check that population is unique
    for p in range(pop_size):
        for q in range(0, p):
            if (p != q): assert (population[p] != population[q])

    print("Minion nets exist?")
    for p in range(pop_size):
            print(population[p].net)

    ''' BOUNDARY CHECK
    if (len(population[p].net.nodes()) > len(population[p].net.edges())):
        print("ERROR in minion: too many nodes")
    elif (2*len(population[p].net.nodes()) < len(population[p].net.edges())):
        print("ERROR in minion: too many edges")
    '''
