import os, pickle, time, shutil
from random import SystemRandom as sysRand
from time import sleep
import fitness, minion, output, plot_nets, net_generator, pressurize, util, init, probabilistic_entropy, bias


#MASTER EVOLUTION
def evolve_master(configs):
    # get configs
    num_workers = int(configs['number_of_workers'])
    output_dir = configs['output_directory']
    worker_pop_size = int(configs['num_worker_nets'])
    fitness_direction = str(configs['fitness_direction'])
    biased = util.boool(configs['biased'])
    num_sims = int(configs['num_sims'])

    population, gen, size, advice, BD_table, num_survive, keep_running = init_run(configs)

    while keep_running:
        t_start = time.time()
        pop_size, num_survive = curr_gen_params(size, num_survive, configs)
        output.master_info(population, gen, size, pop_size, num_survive, advice, BD_table, configs)
        write_mpi_info(output_dir, gen)

        if biased: biases = bias.gen_biases(configs) #all nets must have same bias to have comparable fitness
        else: biases = None

        distrib_workers(population, gen, worker_pop_size, num_survive, advice, BD_table, biases, configs)

        report_timing(t_start, gen, output_dir)
        population = watch(configs, gen, num_workers, output_dir, num_survive, fitness_direction)

        size = len(population[0].net.nodes())
        gen += 1

        keep_running = util.test_stop_condition(size, gen, configs)

    with open(output_dir + "/progress.txt", 'w') as out: out.write("Done")
    output.final_master_info(population, gen, configs)
    del_mpi_dirs(output_dir)

    util.cluster_print(output_dir,"Evolution finished, generating images.")
    if (num_sims == 1): plot_nets.single_run_plots(output_dir)

    util.cluster_print(output_dir,"Master finished config file.\n")






################################ INIT HELPER FUNCTIONS ################################
def init_run(configs):
    num_workers = int(configs['number_of_workers'])
    output_dir = configs['output_directory']
    init_type = str(configs['initial_net_type'])
    start_size = int(configs['starting_size'])
    fitness_direction = str(configs['fitness_direction'])
    num_instance_output = int(configs['num_instance_output'])
    instance_file = configs['instance_file']
    if (num_instance_output==0): instance_file = None

    population, gen, size, advice, BD_table, keep_running = None, None, None, None, None, None #avoiding annoying warnings

    pop_size, num_survive = curr_gen_params(start_size, None, configs)
    util.cluster_print(output_dir,"Master init: num survive: " + str(num_survive) + " out of total popn of " + str(pop_size))
    prog_path = output_dir + "/progress.txt"
    cont=False


    if os.path.isfile(prog_path):
        with open(prog_path) as file:
            gen = file.readline()

        if (gen == 'Done'):
            util.cluster_print(output_dir, "Run already finished, exiting...\n")
            return

        elif (gen and gen!=0 and gen!=1 and gen!=2): #IS CONTINUATION RUN
            gen = int(gen)-2 #latest may not have finished
            population = parse_worker_popn(num_workers, gen, output_dir, num_survive, fitness_direction)
            size = len(population[0].net.nodes())
            gen += 1

            keep_running = util.test_stop_condition(size, gen, configs)
            cont = True

    if not cont: #FRESH START
        init_dirs(num_workers, output_dir)
        output.init_csv(output_dir, configs)
        # draw_nets.init(output_dir)

        population = net_generator.init_population(init_type, start_size, pop_size, configs)
        advice = init.build_advice(population[0].net, configs)
        if (configs['edge_state'] == 'probabilistic' and (util.boool(configs['use_knapsack']) == False)):
            BD_table = probabilistic_entropy.build_BD_table(configs)
        else:
            BD_table = None

        #init fitness eval
        pressurize.pressurize(configs, population[0],instance_file + "Xitern0.csv", advice, BD_table)

        gen, size = 0, start_size
        keep_running = util.test_stop_condition(size, gen, configs)

    return population, gen, size, advice, BD_table, num_survive, keep_running


def init_dirs(num_workers, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    dirs = ["/instances/", "/nets/", "/bias/", "/pickle_nets/", "/to_workers/", "/to_master/", "/pickle_nets/"]
    for dirr in dirs:
        if not os.path.exists(output_dir + dirr):
            os.makedirs(output_dir+dirr)


################################ MPI-RELATED HELPER FUNCTIONS ################################
def write_mpi_info(output_dir, gen):

    with open(output_dir + "/progress.txt", 'w') as out:
        out.write(str(gen))
    #util.cluster_print(output_dir, 'Master wrote progress.txt, now checking dir: ' + str(output_dir + "/to_workers/" + str(itern)))
    if not os.path.exists(output_dir + "/to_workers/" + str(gen)):
        os.makedirs(output_dir + "/to_workers/" + str(gen))
    if not os.path.exists(output_dir + "/to_master/" + str(gen)):
        os.makedirs(output_dir + "/to_master/" + str(gen))

    #del old gen dirs
    prev_gen = gen - 3 #safe since cont starts at itern - 2
    if os.path.exists(output_dir + "/to_master/" + str(prev_gen)):
        shutil.rmtree(output_dir + "/to_master/" + str(prev_gen))
    if os.path.exists(output_dir + "/to_workers/" + str(prev_gen)):
        shutil.rmtree(output_dir + "/to_workers/" + str(prev_gen))


def distrib_workers(population, gen, worker_pop_size, num_survive, advice, BD_table, biases, configs):
    num_workers = int(configs['number_of_workers'])
    output_dir = configs['output_directory']
    debug = util.boool(configs['debug'])

    if (debug == True):  # sequential debug
        for w in range(1, num_workers + 1):
            dump_file = output_dir + "to_workers/" + str(gen) + "/" + str(w)
            seed = population[0].copy()
            randSeeds = os.urandom(sysRand().randint(0, 1000000))
            worker_args = [0, seed, worker_pop_size, min(worker_pop_size, num_survive), randSeeds, advice, BD_table, biases, configs]
            with open(dump_file, 'wb') as file:
                pickle.dump(worker_args, file)
            # pool.map_async(minion.evolve_minion, (dump_file,))
            minion.evolve_minion(dump_file, gen, 0, output_dir)
            sleep(.0001)

    else:
        for w in range(1, num_workers + 1):
            dump_file = output_dir + "/to_workers/" + str(gen) + "/" + str(w)
            seed = population[w % num_survive].copy()
            randSeeds = os.urandom(sysRand().randint(0, 1000000))
            assert (seed != population[w % num_survive])
            worker_args = [w, seed, worker_pop_size, min(worker_pop_size, num_survive), randSeeds, advice, BD_table, biases, configs]
            with open(dump_file, 'wb') as file:
                pickle.dump(worker_args, file)

    del population
    if (debug == True): util.cluster_print(output_dir, "debug is ON")


def parse_worker_popn (num_workers, gen, output_dir, num_survive, fitness_direction):
    popn = []
    print('master.parse_worker_popn(): num workers = ' + str(num_workers) + " and gen " + str(gen))
    print("parse worker pop params: dir = " + str(output_dir) + ".")
    for w in range(1,num_workers+1): 
        dump_file = output_dir + "/to_master/" + str(gen) + "/" + str(w)
        with open(dump_file, 'rb') as file:
            worker_pop = pickle.load(file)
        i=0
        for indiv in worker_pop:
            popn.append(indiv)
            i+=1

    sorted_popn = fitness.eval_fitness(popn, fitness_direction)
    return sorted_popn[:num_survive]


def watch(configs, gen, num_workers, output_dir, num_survive, fitness_direction):

    dump_dir = output_dir + "/to_master/" + str(gen)
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
                            dump_file = output_dir + "/to_master/" + str(gen) + "/" + str(f)
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
    if (gen % 100 == 0): util.cluster_print(output_dir,"master finished extracting workers after " + str(time_elapsed) + " seconds, and making " + str(dir_checks) + " dir checks.")

    return popn


def del_mpi_dirs(output_dir):
    shutil.rmtree(output_dir + "/to_master/")
    shutil.rmtree(output_dir + "/to_workers/")


################################ MISC HELPER FUNCTIONS ################################
def curr_gen_params(size, prev_num_survive, configs):
    #could add dynam worker_pop_size Island algo and such
    num_workers = int(configs['number_of_workers'])
    survive_percent = float(configs['percent_survive'])
    survive_fraction = float(survive_percent) / 100
    worker_pop_size = int(configs['num_worker_nets'])

    pop_size = worker_pop_size * num_workers
    num_survive = int(pop_size * survive_fraction)
    if (num_survive < 1):  num_survive = 1
    if (prev_num_survive):
        if (num_survive > prev_num_survive): num_survive = prev_num_survive

    return pop_size, num_survive


def report_timing(t_start, gen, output_dir, report_freq=.001):
    if report_freq == 0: return
    t_end = time.time()
    t_elapsed = t_end - t_start
    if (gen % int(1 / report_freq) == 0): util.cluster_print(output_dir, "Master finishing after " + str(t_elapsed) + " seconds.\n")

