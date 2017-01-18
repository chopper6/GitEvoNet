# worker processes

import math, pickle
import output, mutate, fitness, pressurize

def evolve_minion(worker_file):
    with open(str(worker_file), 'rb') as file:
        worker_ID, seed, worker_gens, pop_size, num_return, randSeeds, configs = pickle.load(file)
        file.close()

    population = gen_population_from_seed(seed, pop_size)
    start_size = len(seed.net.nodes())

    fitness_type = int(configs['fitness_type'])
    survive_fraction = float(configs['percent_survive'])/100
    num_survive = survive_fraction * pop_size
    output_dir = configs['output_directory'].replace("v4nu_minknap_1X_both_reverse/", '')
    output_dir += str(worker_ID)

    solver_time = 0

    for g in range(worker_gens):
        if (g != 0):
            for p in range(num_survive,pop_size):
                population[p] = population[p%num_survive]
                assert (population[p] != population[p%num_survive])
                assert (population[p].net != population[p % num_survive].net)

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
            mutate.mutate(configs, population[p].net, randSeeds[g*pop_size + p])

            pressure_results = pressurize.pressurize(configs, population[p].net)
            population[p].fitness_parts[0], population[p].fitness_parts[1], solver_time = pressure_results[0], pressure_results[1], pressure_results[2]

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
        fitness.eval_fitness(population, fitness_type)

    write_out_worker(worker_file, population, num_return)

    # some output
    if (worker_ID == 0):
        orig_dir = configs['output_directory'].replace("v4nu_minknap_1X_both_reverse/", '')
        end_size = len(population[0].net.nodes())
        growth = end_size - start_size
        output.minion_csv(orig_dir, solver_time, growth, end_size)


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
