# worker processes

import math, pickle, random, os, time
import output, fitness, pressurize, mutate, init
from time import process_time as ptime

def work(batch_dir, rank):

    print ("\t\t\t\tworker #"+str(rank)+" is working,\t")
    progress = batch_dir + "/progress.txt"

    done = False
    gen = 0
    prev_dir = None
    while not done:
        t_start = time.time()
        while not os.path.isfile (progress): # master will create this file
            time.sleep(.2)

        if (os.path.getmtime(progress) + .5 < time.time()): #check that file has not been recently touched
            with open(progress, 'r') as file:
                lines = file.readlines()
                if (lines):
                    if (lines[0] == 'Done' or lines[0] == 'Done\n'):
                        print("Worker #" + str(rank) + " + exiting.")
                        return  # no more work to be done

                if (len(lines) > 1): #encompasses 'loading next config' condition, since wait for next

                    dirr = lines[0].strip()

                    #reset gen for new config file (indicated by diff directory)
                    if (prev_dir != dirr): gen = 0
                    prev_dir = dirr

                    #print("worker using dir: " + str(dirr))
                    #print("worker() progress lines: " + str(lines))
                    global_gen = int(lines[-1].strip())
                    #print("worker using gen: " + str(gen) + ", while global gen = " + str(global_gen))
                    if (len(lines) > 2):
                        if (lines[-1] == 'continue'):
                            print("Worker #" + str(rank) + " recognizes continue command.")
                            gen = global_gen

                    if (gen == global_gen):

                        worker_args = str(batch_dir) + "/to_workers/" + str(gen) + "/" + str(rank)
                        #print("worker looking for file: " + str(worker_args))
                        while not os.path.isfile(worker_args):
                            time.sleep(2)

                        t_end = time.time()
                        t_elapsed = t_end - t_start
                        print("Worker # " + str(rank) + " starting evolution after waiting " + str(t_elapsed) + " seconds. Starts at gen " + str(gen))
                        evolve_minion(worker_args, gen, rank, batch_dir)
                        gen+=1

                    #else: print("minion.work(): worker gen = " + str(gen) + ", while global gen = " + str(global_gen))



def evolve_minion(worker_file, gen, rank, orig_dir):
    t_start = time.time()

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

            if (control == None):
                pressure_results = pressurize.pressurize(configs, population[p].net, None)  # false: don't track node fitness, None: don't write instances to file
                population[p].fitness_parts[0], population[p].fitness_parts[1], population[p].fitness_parts[2] = pressure_results[0], pressure_results[1], pressure_results[2]

            else: print("ERROR in minion(): unknown control config: " + str(control))

        old_popn = population
        population = fitness.eval_fitness(old_popn)
        del old_popn
        #debug(population,worker_ID)
        curr_gen += 1
    write_out_worker(orig_dir + "/to_master/" + str(gen) + "/" + str(rank), population, num_return)
    
    # some output
    if (worker_ID == 0):
        orig_dir = configs['output_directory']
        end_size = len(population[0].net.nodes())
        growth = end_size - start_size
        output.minion_csv(orig_dir, pressurize_time, growth, end_size)
        #debug(population, worker_ID)
        #if (worker_ID==0): print("Pressurizing took " + str(pressurize_time) + " secs, while mutate took " + str(mutate_time) + " secs.")

    t_end = time.time()
    time_elapsed = t_end - t_start
    print("Worker #" + str(rank) + " finishing after " + str(time_elapsed) + " seconds")


def write_out_worker(worker_file, population, num_return):
    # overwrite own input file with return population
    #print("worker writing out to " + str(worker_file) + "\n")
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
