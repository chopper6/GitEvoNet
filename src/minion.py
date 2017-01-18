# worker processes

import math, pickle
from time import process_time as ptime
import time
from ctypes import cdll
import output, mutate, fitness, pressurize
from pympler.tracker import SummaryTracker

def evolve_minion(worker_file):
    t0 = ptime()
    i0 = time.time()
    with open(str(worker_file), 'rb') as file:
        worker_ID, seed, worker_gens, curr_master_gen, gens_per_growth, num_survive, master_gens, configs = pickle.load(file)
        file.close()

    population = gen_population_from_seed(seed, num_survive)
    start_size = len(seed.net.nodes())

    pressure = math.ceil((float(configs['PT_pairs_dict'][1][0]) / 100.0))
    tolerance = configs['PT_pairs_dict'][1][1]
    mutation_freq = float(configs['mutation_frequency'])
    sampling_rounds = int(configs['sampling_rounds'])
    max_sampling_rounds = int(configs['sampling_rounds_max'])
    knapsack_solver = cdll.LoadLibrary(configs['KP_solver_binary'])
    fitness_type = int(configs['fitness_type'])

    mutation_bias = str(configs['mutation_bias'])
    if (mutation_bias == "True"):
        mutation_bias = True
    elif (mutation_bias == "False"):
        mutation_bias = False
    else:
        print("Error in configs: mutation_bias should be True or False.")

    survive_percent = int(configs['percent_survive'])
    survive_fraction = float(survive_percent) / 100

    output_dir = configs['output_directory'].replace("v4nu_minknap_1X_both_reverse/", '')
    output_dir += str(worker_ID)

    pop_size = num_survive  # for current build
    t1 = ptime()
    i1 = time.time()
    init_t = i1 - i0
    growth_t, mutate_t, pressure_t, eval_t, replic_t = 0, 0, 0, 0, 0
    num_growth = 0

    #tracker2 = SummaryTracker()
    for g in range(worker_gens):
        # worker replication
        #if (worker_ID==0):  tracker2.print_diff()  
        t0 = ptime()
        #TODO: add replication, ensure del
        t1 = ptime()
        replic_t += t1 - t0

        '''
        if (worker_ID == 0):
            print ("Minion population fitness: ")
            for p in range(pop_size):
                print(population[p].fitness)
        '''
        # check that population is unique
        for p in range(pop_size):
            for q in range(0, p):
                if (p != q): assert (population[p] != population[q])

        for p in range(pop_size):
            # mutation
            t0 = ptime()
            i0 = time.time()
            mutate.mutate(configs, population[p].net)
            t1 = ptime()
            i1 = time.time()
            #mutate_t += t1 - t0
            mutate_t += i1-i0

            t0 = ptime()
            i0 = time.time()
            num_samples_relative = min(max_sampling_rounds, len(population[p].net.nodes()) * sampling_rounds)
            pressure_relative = int(pressure * len(population[p].net.nodes()))
            population[p].fitness_parts = pressurize.pressurize(configs, population[p].net, pressure_relative, tolerance, knapsack_solver, fitness_type, num_samples_relative)
            t1 = ptime()
            i1 = time.time()
            #pressure_t += t1 - t0
            pressure_t += i1-i0
            ''' FITNESS CHECK
            if (worker_ID == 0 and p==0):
                print ("Minion population fitness: ")
                for p in range(pop_size):
                    print(population[p].fitness)
            '''
            ''' BOUNDARY CHECK
            if (len(population[p].net.nodes()) > len(population[p].net.edges())):
                print("ERROR in minion: too many nodes")
            elif (2*len(population[p].net.nodes()) < len(population[p].net.edges())):
                print("ERROR in minion: too many edges")
            '''
        t0 = ptime()
        i0 = time.time()
        fitness.eval_fitness(population, fitness_type)
        t1 = ptime()
        i1 = time.time()
        #eval_t += t1 - t0
        eval_t += i1 - i0

    i0 = time.time()
    t0 = ptime()
    write_out_worker(worker_file, population, num_survive)
    t1 = ptime()
    i1 = time.time()
    write_t = t1 - t0
    write_t = i1 - i0
    # some output
    if (worker_ID == 0 and curr_master_gen == 0):
        
        print("\nminion init took " + str(init_t) + " sec.")
        print("minion replication took " + str(replic_t) + " sec.")
        print("minion growth took " + str(growth_t) + " sec.")
        print("minion mutate took " + str(mutate_t) + " sec.")
        print("minion pressurize took " + str(pressure_t) + " sec.")
        print("minion eval fitness took " + str(eval_t) + " sec.")
        print("minion write took " + str(write_t) + " sec.\n")
        
        orig_dir = configs['output_directory'].replace("v4nu_minknap_1X_both_reverse/", '')
        end_size = len(population[0].net.nodes())
        growth = end_size - start_size
        output.minion_csv(orig_dir, pressure_t, master_gens, growth, end_size)


def write_out_worker(worker_file, population, num_survive):
    # overwrite own input file with return population
    with open(worker_file, 'wb') as file:
        pickle.dump(population[:num_survive], file)
        file.close()

def gen_population_from_seed(seed, num_survive):
    population = []
    for p in range(num_survive):
        population.append(seed.copy())
        assert(population[-1] != seed)
    return population
