import math, os, pickle, sys, time, shutil
from random import SystemRandom as sysRand
from time import sleep, process_time
import networkx as nx
import fitness, minion, output, plot_nets, net_generator, perturb, pressurize, draw_nets, plot_fitness, node_fitness, mutate, util

def evolve_master(configs):
    protocol = configs['protocol']
    output_dir = configs['output_directory']
    if (protocol == 'from seed'):
        evolve_from_seed(configs)
    else:
        util.cluster_print(output_dir,"ERROR in master(): unknown protocol " + str(protocol))
    return

def evolve_from_seed(configs):
    # get configs
    num_workers = int(configs['number_of_workers'])
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

    size, total_gens, itern, population, num_survive = None, None, None, None, None #just to avoid annoying warnings

    worker_pop_size, pop_size, num_survive, worker_gens = curr_gen_params(start_size, end_size, num_workers,survive_fraction, -1, worker_pop_size_config)
    util.cluster_print(output_dir,"Master init worker popn size: " + str(worker_pop_size) + ",\t num survive: " + str(num_survive) + " out of total popn of " + str(pop_size))

    prog_path = output_dir + "/progress.txt"
    cont=False
    if os.path.isfile(prog_path):
        with open(prog_path) as file:
            itern = file.readline()

        if (itern): #IS CONTINUATION RUN
            itern = int(itern)-2 #fall back one, latest may not have finished
            population = parse_worker_popn(num_workers, itern, output_dir, num_survive)
            size = len(population[0].net.nodes())
            itern += 1
            total_gens = itern  # also temp, assumes worker gens = 1
            util.cluster_print(output_dir,"\nmaster(): CONTINUE RUN with global gen = " + str(itern) + " \n")
            cont = True

    if cont==False: #FRESH START
        init_dirs(num_workers, output_dir)
        output.init_csv(output_dir, configs)
        # draw_nets.init(output_dir)

        population = net_generator.init_population(init_type, start_size, pop_size, configs)
        # init fitness, uses net0 since effectively a random choice (may disadv init, but saves lotto time)

        #init fitness eval
        pressure_results = pressurize.pressurize(configs, population[0].net,instance_file + "Xitern0.csv")  # false: don't track node fitness, None: don't write instances to file
        population[0].fitness_parts[0], population[0].fitness_parts[1], population[0].fitness_parts[2] = pressure_results[0], pressure_results[1], pressure_results[2]
        fitness.eval_fitness([population[0]])
        output.deg_change_csv([population[0]], output_dir)

        total_gens, size, itern = 0, start_size, 0

    estim_wait = None
    while (size <= end_size and total_gens < max_gen):
        t_start = time.time()
        worker_pop_size, pop_size, num_survive, worker_gens = curr_gen_params(size, end_size, num_workers, survive_fraction, num_survive, worker_pop_size_config)

        #OUTPUT INFO
        if (itern % int(max_gen / num_output) == 0):
            output.to_csv(population, output_dir, total_gens)
            util.cluster_print(output_dir,"Master at gen " + str(total_gens) + ", with net size = " + str(size) + " nodes and " + str(len(population[0].net.edges())) + " edges, " + str(num_survive) + "<=" + str(len(population)) + " survive out of " + str(pop_size))
            worker_percent_survive = worker_pop_size #should match however workers handle %survive
            util.cluster_print(output_dir,"Workers: over " + str(worker_gens) + " gens " + str(worker_percent_survive) + " nets survive out of " + str(worker_pop_size) + ".\n")

            nx.write_edgelist(population[0].net, output_dir+"/fittest_net.edgelist")

        if (num_instance_output != 0):
            if (itern % int(max_gen / num_instance_output) == 0):
                # if first gen, have already pressurized w/net[0]
                if (itern != 0): pressure_results = pressurize.pressurize(configs, population[0].net, instance_file + "Xitern" + str( itern) + ".csv")

        #if (itern % int(max_gen / num_draw) == 0 and num_draw != 0 ):
            #draw_nets.basic(population, output_dir, total_gens, draw_layout)

        if (itern % int(max_gen/num_net_output) ==0):
            nx.write_edgelist(population[0].net, output_dir + "/nets/" + str(itern))

        if (num_grow != 0): #WILL NOT WORK WELL WITH ISLAND ALGO, OR MULT WORKER GENS
            #ASSUMES GROWTH ONLY FOR 1st HALF
            rate = int(max_gen/(2*num_grow))
            if ((itern-start_size) % rate ==0 and itern < (max_gen/2 - start_size*rate)):
                for p in range(len(population)):
                    mutate.add_nodes(population[p].net, 1, edge_node_ratio)


        write_mpi_info(output_dir, itern)
        #debug(population), outdated

        # distribute workers
        if (debug == True): #sequential debug, may be outdated
            dump_file = output_dir + "to_workers/" + str(itern) + "/0"
            seed = population[0].copy()
            randSeeds = os.urandom(sysRand().randint(0, 1000000))
            worker_args = [0, seed, worker_gens, worker_pop_size, min(worker_pop_size, num_survive), randSeeds,total_gens, configs]
            with open(dump_file, 'wb') as file:
                pickle.dump(worker_args, file)
            #pool.map_async(minion.evolve_minion, (dump_file,))
            minion.evolve_minion(dump_file)
            sleep(.0001)

        else:
            for w in range(0,num_workers):
                dump_file =  output_dir + "/to_workers/" + str(itern) + "/" + str(w)
                #util.cluster_print(output_dir,"master dumping to file: " + str(dump_file))
                seed = population[w % num_survive].copy()
                randSeeds = os.urandom(sysRand().randint(0,1000000))
                assert(seed != population[w % num_survive])
                worker_args = [w, seed, worker_gens, worker_pop_size, min(worker_pop_size,num_survive), randSeeds, total_gens, configs]
                with open(dump_file, 'wb') as file:
                    pickle.dump(worker_args, file)

            #don't waste threads, master exe a worker gen
            dump_file = output_dir + "/to_workers/" + str(itern) + "/0"
            return_file = output_dir + "/to_master/" + str(itern) + "/0"
            minion.evolve_minion(dump_file, itern, 0, return_file)

        del population
        if (debug == True):
            util.cluster_print(output_dir,"debug is ON")
            num_workers, num_survive = 1,1


        t_end = time.time()
        t_elapsed = t_end-t_start
        util.cluster_print(output_dir,"Master finishing after " + str(t_elapsed) + " seconds.\n")
        estim_wait = watch(configs, itern, num_workers, output_dir, estim_wait)
        population = parse_worker_popn(num_workers, itern, output_dir, num_survive)
        size = len(population[0].net.nodes())
        itern += 1
        total_gens += worker_gens

    with open(output_dir + "/progress.txt", 'w') as out:
        out.write("Done")

    #final outputs
    nx.write_edgelist(population[0].net, output_dir+"/nets/"+str(itern))

    output.to_csv(population, output_dir, total_gens)
    output.deg_change_csv(population, output_dir)
    #draw_nets.basic(population, output_dir, total_gens, draw_layout)

    util.cluster_print(output_dir,"Evolution finished, generating images.")
    plot_nets.single_run_plots(output_dir)
    #instances.analyze(output_dir)

    util.cluster_print(output_dir,"Master finished config file.\n")
    return


def init_dirs(num_workers, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    dirs = ["/node_info/", "/instances/", "/nets/", "/to_workers/", "/to_master/"]
    for dirr in dirs:
        if not os.path.exists(output_dir + dirr):
            os.makedirs(output_dir+dirr)


def parse_worker_popn (num_workers, itern, output_dir, num_survive):
    popn = []
    print('master.parse_worker_popn(): num workers = ' + str(num_workers) + " and itern " + str(itern))
    for w in range(0,num_workers): 
        dump_file = output_dir + "/to_master/" + str(itern) + "/" + str(w)
        with open(dump_file, 'rb') as file:
            worker_pop = pickle.load(file)
        i=0
        for indiv in worker_pop:
            popn.append(indiv)
            i+=1

    sorted_popn = fitness.eval_fitness(popn)
    return sorted_popn[:num_survive]


def curr_gen_params(size, end_size, num_workers, survive_fraction, prev_num_survive, worker_pop_size_config):
    #could add dynam worker_pop_size Island algo and such

    worker_pop_size = math.floor(end_size/size) #not used
    worker_gens = 1
    # ISLAND #
    # percent_size = float(size) / float(end_size)
    # math.ceil(10 * math.pow(math.e, -4 * percent_size))

    pop_size = worker_pop_size_config * num_workers
    num_survive = int(pop_size * survive_fraction)
    if (num_survive < 1):  num_survive = 1
    if (prev_num_survive > 0):
        if (num_survive > prev_num_survive):   num_survive = prev_num_survive

    return worker_pop_size_config, pop_size, num_survive, worker_gens


def debug(population):
    '''
    util.cluster_print(output_dir,"Master population fitness: ")
    for p in range(len(population)):
        util.cluster_print(output_dir,population[p].fitness)
    '''
    # check that population is unique
    for p in range(len(population)):
        for q in range(0, p):
            if (p != q): assert (population[p] != population[q])



def watch(configs, itern, num_workers, output_dir, estim_wait):

    dump_dir = output_dir + "/to_master/" + str(itern)

    done, i = False, 1

    t_start = time.time()
    estim_used = False
    while not done:
        if (estim_wait != None and estim_used == False): 
            time.sleep(estim_wait + .1)
            estim_used = True
        elif(estim_wait != None): 
            time.sleep(.1)
            estim_wait += .1
        else: time.sleep(.1)  #freq checks for accurate estim_wait
        i += 1
        #util.cluster_print(output_dir,dump_dir)
        for root, dirs, files in os.walk(dump_dir):
            #util.cluster_print(output_dir,str(dump_dir) + " has " + str(len(files)) + " files in it.")
            if (len(files) == num_workers):
                for f in files:
                    if (os.path.getmtime(root + "/" + f) + .5 > time.time()): break #file may still be being written

                t_end = time.time()
                time_elapsed = t_end - t_start
                if (estim_wait == None): 
                    estim_wait = time_elapsed
                    print("master using estim_wait = " + str(estim_wait))
                if (estim_used == True): print("master updated estim_wait to " + str(estim_wait))
                util.cluster_print(output_dir,"master continuing after waiting for " + str(time_elapsed) + " seconds, and making " + str(i) + " dir checks.")
                return estim_wait


def write_mpi_info(output_dir, itern):

    #os.rename(output_dir + "/progress*.txt", output_dir + "/progress_" + str(itern) + ":w.txt")

    #if (itern ==0):
    #    with open(output_dir + "/progress.txt", 'w') as out:
    #        out.write(output_dir + "\n")

    with open(output_dir + "/progress.txt", 'w') as out:
        out.write(str(itern))
    #util.cluster_print(output_dir, 'Master wrote progress.txt, now checking dir: ' + str(output_dir + "/to_workers/" + str(itern)))
    if not os.path.exists(output_dir + "/to_workers/" + str(itern)):
        os.makedirs(output_dir + "/to_workers/" + str(itern))
    if not os.path.exists(output_dir + "/to_master/" + str(itern)):
        os.makedirs(output_dir + "/to_master/" + str(itern))


    #del old gen dirs
    prev_itern = itern - 3 #safe since cont starts at itern - 2
    if os.path.exists(output_dir + "/to_master/" + str(prev_itern)):
        shutil.rmtree(output_dir + "/to_master/" + str(prev_itern))
    if os.path.exists(output_dir + "/to_workers/" + str(prev_itern)):
        shutil.rmtree(output_dir + "/to_workers/" + str(prev_itern))

    #else: util.cluster_print(output_dir,"WARNING in master.write_mpi_info(): dir /to_master/" + str(itern) + " already exists...sensible if a continuation run.")
