import math, os, pickle, time, shutil
from random import SystemRandom as sysRand
from time import sleep
import networkx as nx
import fitness, minion, output, plot_nets, plot_vs_real, net_generator, perturb, pressurize, draw_nets, mutate, util, plot_undir, init, probabilistic_entropy, bias



def evolve_master(configs):
    protocol = configs['protocol']
    protocol_configs(protocol, configs) #basically just auto-sets certain params
    evolve_population(configs)


def protocol_configs(protocol, configs): #TODO: update these to useful protocols, will also fully sep Info and Kp projects
    output_dir = configs['output_directory']

    if (protocol == 'mLmH'):
        configs['leaf_metric'] = 'RGAR'
        configs['leaf_operation'] = 'sum'
        configs['leaf_power'] = 2

        configs['hub_metric'] = 'ETB'
        configs['hub_operation'] = 'Btot'

        configs['fitness_operation'] = 'multiply'
        configs['fitness_direction'] = 'max'

        configs['num_sims'] = 1
        configs['advice_creation'] = 'each'

    elif (protocol == 'direct evo' or protocol == 'direct evolution' or protocol == 'direct'):
        configs['hub_metric'] = 'Bin'
        configs['hub_operation'] = 'Btot'
        configs['fitness_operation'] = 'hub'
        configs['fitness_direction'] = 'max'
        configs['advice_creation'] = 'once'

    elif (protocol == 'entropy'):
        configs['leaf_metric'] = 'entropy'
        configs['fitness_operation'] = 'product'
        configs['fitness_direction'] = 'min'

        configs['num_sims'] = 1
        configs['advice_creation'] = 'each'

    elif (protocol == 'custom'):
         util.cluster_print(output_dir, "Custom run, careful to define all parameters.\n")

    else:
        util.cluster_print(output_dir, "ERROR: in master: unknown protocol " + str(protocol))



def evolve_population(configs):
    # get configs
    num_workers = int(configs['number_of_workers'])
    output_dir = configs['output_directory']
    survive_percent = float(configs['percent_survive'])
    survive_fraction = float(survive_percent) / 100
    num_output = int(configs['num_output'])
    num_net_output = int(configs['num_net_output'])
    max_gen = int(configs['max_generations'])
    debug = util.boool(configs['debug'])
    worker_pop_size_config = int(configs['num_worker_nets'])
    init_type = str(configs['initial_net_type'])
    start_size = int(configs['starting_size'])
    end_size = int(configs['ending_size'])
    fitness_direction = str(configs['fitness_direction'])
    num_instance_output = int(configs['num_instance_output'])
    instance_file = configs['instance_file']
    biased = util.boool(configs['biased'])
    if (num_instance_output==0): instance_file = None
    num_sims = int(configs['num_sims'])

    worker_pop_size, pop_size, num_survive, worker_gens = curr_gen_params(start_size, end_size, num_workers,survive_fraction, -1, worker_pop_size_config)
    util.cluster_print(output_dir,"Master init worker popn size: " + str(worker_pop_size) + ",\t num survive: " + str(num_survive) + " out of total popn of " + str(pop_size))
    prog_path = output_dir + "/progress.txt"
    cont=False

    if (configs['edge_state'] == 'probabilistic' and (util.boool(configs['use_knapsack']) == False)): BD_table = probabilistic_entropy.build_BD_table(configs)
    else: BD_table = None

    if os.path.isfile(prog_path):
        with open(prog_path) as file:
            itern = file.readline()

        if (itern == 'Done'):
            util.cluster_print(output_dir, "Run already finished, exiting...\n")
            return

        elif (itern and itern!=0 and itern!=1 and itern!=2): #IS CONTINUATION RUN
            itern = int(itern)-2 #latest may not have finished
            population = parse_worker_popn(num_workers, itern, output_dir, num_survive, fitness_direction)
            size = len(population[0].net.nodes())
            itern += 1
            total_gens = itern  # also temp, assumes worker gens = 1

            a_worker_file = output_dir + "/to_workers/" + str(itern) + "/1"
            with open(a_worker_file, 'rb') as w_file:
                a_worker_ID, a_seed, a_worker_gens, a_pop_size, a_num_return, a_randSeed, a_curr_gen, advice, BD_table, biases,  a_configs = pickle.load(w_file)

            cont = True

    if cont==False: #FRESH START
        init_dirs(num_workers, output_dir)
        output.init_csv(output_dir, configs)
        # draw_nets.init(output_dir)

        population = net_generator.init_population(init_type, start_size, pop_size, configs)
        advice = init.build_advice(population[0].net, configs)

        #init fitness eval
        pressure_results = pressurize.pressurize(configs, population[0].net,instance_file + "Xitern0.csv", advice, BD_table)
        population[0].fitness_parts[0], population[0].fitness_parts[1], population[0].fitness_parts[2] = pressure_results[0], pressure_results[1], pressure_results[2]
        fitness.eval_fitness([population[0]], fitness_direction)
        output.deg_change_csv([population[0]], output_dir)

        total_gens, size, itern = 0, start_size, 0

    while (size < end_size and total_gens < max_gen):
        # size < end_size --> no more adaptation after growth
        t_start = time.time()
        worker_pop_size, pop_size, num_survive, worker_gens = curr_gen_params(size, end_size, num_workers, survive_fraction, num_survive, worker_pop_size_config)

        #OUTPUT INFO
        if (itern % int(max_gen / num_output) == 0):
            output.popn_data(population, output_dir, total_gens)
            util.cluster_print(output_dir,"Master at gen " + str(total_gens) + ", with net size = " + str(size) + " nodes and " + str(len(population[0].net.edges())) + " edges, " + str(num_survive) + "<=" + str(len(population)) + " survive out of " + str(pop_size))
            nx.write_edgelist(population[0].net, output_dir+"/fittest_net.edgelist")

        if (num_instance_output != 0):
            if (itern % int(max_gen / num_instance_output) == 0):
                # if first gen, have already pressurized w/net[0]
                if (itern != 0): pressure_results = pressurize.pressurize(configs, population[0].net, instance_file + "Xitern" + str( itern) + ".csv", advice, BD_table)

        if (itern % int(max_gen/num_net_output) == 0): #TODO: merge this with above output, poss new save_net fn() in output.py
            nx.write_edgelist(population[0].net, output_dir + "/nets/" + str(itern))
            pickle_file =  output_dir + "/pickle_nets/" + str(itern) + "_pickle"
            with open(pickle_file, 'wb') as file:
                pickle.dump(population[0].net, file)

        write_mpi_info(output_dir, itern)

        if biased: biases = bias.gen_biases(itern/max_gen, configs)
        else: biases = None

        # distribute workers
        if (debug == True): #sequential debug, may be outdated
            dump_file = output_dir + "to_workers/" + str(itern) + "/1"
            seed = population[0].copy()
            randSeeds = os.urandom(sysRand().randint(0, 1000000))
            worker_args = [0, seed, worker_gens, worker_pop_size, min(worker_pop_size, num_survive), randSeeds,total_gens, advice, BD_table, biases, configs]
            with open(dump_file, 'wb') as file:
                pickle.dump(worker_args, file)
            #pool.map_async(minion.evolve_minion, (dump_file,))
            minion.evolve_minion(dump_file, itern, 0, output_dir)
            sleep(.0001)

        else:
            for w in range(1,num_workers+1):
                dump_file =  output_dir + "/to_workers/" + str(itern) + "/" + str(w)
                seed = population[w % num_survive].copy()
                randSeeds = os.urandom(sysRand().randint(0,1000000))
                assert(seed != population[w % num_survive])
                worker_args = [w, seed, worker_gens, worker_pop_size, min(worker_pop_size,num_survive), randSeeds, total_gens, advice, BD_table, biases, configs]
                with open(dump_file, 'wb') as file:
                    pickle.dump(worker_args, file)

        del population
        if (debug == True):
            util.cluster_print(output_dir,"debug is ON")
            num_workers, num_survive = 1,1


        t_end = time.time()
        t_elapsed = t_end-t_start
        if (itern % 100 == 0): util.cluster_print(output_dir,"Master finishing after " + str(t_elapsed) + " seconds.\n")
        population = watch(configs, itern, num_workers, output_dir, num_survive, fitness_direction)

        size = len(population[0].net.nodes())
        itern += 1
        total_gens += worker_gens

    with open(output_dir + "/progress.txt", 'w') as out:
        out.write("Done")

    #final outputs
    nx.write_edgelist(population[0].net, output_dir+"/nets/"+str(itern))
    pickle_file = output_dir + "/pickle_nets/" + str(itern) + "_pickle"
    with open(pickle_file, 'wb') as file: pickle.dump(population[0].net, file)
    output.popn_data(population, output_dir, total_gens)
    #draw_nets.basic(population, output_dir, total_gens, draw_layout)

    shutil.rmtree(output_dir + "/to_master/")
    shutil.rmtree(output_dir + "/to_workers/")

    util.cluster_print(output_dir,"Evolution finished, generating images.")
    if (num_sims == 1):
        plot_nets.single_run_plots(output_dir)
        #plot_vs_real.plot_dir('/',output_dir+':all')

    if util.boool(configs['biased']):
        util.cluster_print(output_dir,"Pickling biases.")
        bias.pickle_bias(population[0].net, output_dir+"/bias", configs['bias_on'])

    util.cluster_print(output_dir,"Master finished config file.\n")


def init_dirs(num_workers, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    dirs = ["/instances/", "/nets/", "/bias/", "/pickle_nets/", "/to_workers/", "/to_master/", "/pickle_nets/"]
    for dirr in dirs:
        if not os.path.exists(output_dir + dirr):
            os.makedirs(output_dir+dirr)

def parse_worker_popn (num_workers, itern, output_dir, num_survive, fitness_direction):
    popn = []
    print('master.parse_worker_popn(): num workers = ' + str(num_workers) + " and itern " + str(itern))
    print("parse worker pop params: dir = " + str(output_dir) + ".")
    for w in range(1,num_workers+1): 
        dump_file = output_dir + "/to_master/" + str(itern) + "/" + str(w)
        with open(dump_file, 'rb') as file:
            worker_pop = pickle.load(file)
        i=0
        for indiv in worker_pop:
            popn.append(indiv)
            i+=1

    sorted_popn = fitness.eval_fitness(popn, fitness_direction)
    return sorted_popn[:num_survive]

def parse_worker (worker_num, itern, output_dir, num_survive):
    #unused
    dump_file = output_dir + "/to_master/" + str(itern) + "/" + str(worker_num)
    with open(dump_file, 'rb') as file:
        worker_pop = pickle.load(file)

    return worker_pop[:num_survive]



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


def watch(configs, itern, num_workers, output_dir, num_survive, fitness_direction):

    dump_dir = output_dir + "/to_master/" + str(itern)
    t_start = time.time()
    popn, num_finished, dir_checks = [], 0,0

    ids = [str(i) for i in range(1, num_workers + 1)]
    while (num_finished < num_workers):
        time.sleep(1)
        dir_checks+=1
        for root, dirs, files in os.walk(dump_dir):
            for f in files:
                if f in ids:
                        if (os.path.getmtime(root + "/" + f) + 1 < time.time()):
                            dump_file = output_dir + "/to_master/" + str(itern) + "/" + str(f)
                            with open(dump_file, 'rb') as file:
                                try:
                                    worker_pop = pickle.load(file)
                                    popn += worker_pop[:num_survive]
                                    num_finished += 1
                                    ids.remove(f)
                                except: pass

            #sort and delete some
            sorted_popn = fitness.eval_fitness(popn, fitness_direction)
            popn = sorted_popn[:num_survive]
            del sorted_popn
    assert (not ids)

    t_end = time.time()
    time_elapsed = t_end - t_start
    if (itern % 100 == 0): util.cluster_print(output_dir,"master finished extracting workers after " + str(time_elapsed) + " seconds, and making " + str(dir_checks) + " dir checks.")

    return popn

def write_mpi_info(output_dir, itern):

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
