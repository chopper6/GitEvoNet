def connect_components(net):
    #finds connected components and connects them
    components = list(nx.weakly_connected_component_subgraphs(net))
    while  (len(components) != 1):
        for i in range(len(components)-1):
            node1 = random.SystemRandom().sample(components[i].nodes(), 1)
            node2 = random.SystemRandom().sample(components[i+1].nodes(), 1)
            sign = random.randint(0, 1)
            if (sign == 0):     sign = -1
            net.add_edge(node1[0], node2[0], sign=sign)

        #since add edge, could over step boundary condition
        if (2*len(net.nodes()) < len(net.edges())):
            #if so, rm an edge
            edge = random.SystemRandom().sample(net.out_edges(), 1)
            edge = edge[0]
            net.remove_edge(edge[0], edge[1])

        components = list(nx.weakly_connected_component_subgraphs(net))


#RETIRED FUNCTIONS (may be of use for reference)
def evolve_island_master(configs):
    #get configs
    crossover_fraction = float(configs['crossover_percent'])/100
    output_dir = configs['output_directory'].replace("v4nu_minknap_1X_both_reverse/", '')  #no idea where this is coming from
    output_freq = float(configs['output_frequency'])
    num_workers = int(configs['number_of_workers'])
    start_size = int(configs['starting_size'])
    survive_percent = int(configs['percent_survive'])
    survive_fraction = float(survive_percent)/100
    pop_size = int(configs['population_size'])
    num_survive = int(round(pop_size*survive_fraction))
    fitness_type = int(configs['fitness_type'])

    #new configs
    master_gens = int(configs['master_generations'])
    init_type = int(configs['initial_net_type'])
    popn_cutoff = (num_survive*num_workers)%pop_size
    if (popn_cutoff == 0): popn_cutoff = pop_size

    num_return = math.floor(pop_size/num_workers)

    init_worker_dirs(num_workers, output_dir)
    output.init_csv(pop_size, num_workers, output_dir, configs)

    #info
    print(str(num_workers) + " workers will evolve a population of " + str(pop_size) + " networks.")
    print (str(int(popn_cutoff/num_workers)) + " individuals will be distributed to each worker.")
    print ("Then each worker will return " + str(num_return) + " individuals.\n")

    population = gen_init_population(init_type, start_size, pop_size)
    eval_fitness(population, fitness_type)

    for g in range(master_gens):
        population.sort(key=operator.attrgetter('fitness'))
        population.reverse()  # MAX fitness function

        if (g == 0 or g % int(1 / output_freq) == 0):
            output.to_csv(population, output_dir)
        breed(population, num_survive, pop_size, crossover_fraction) #maybe cross all

        #to randomize worker allocations
        random.shuffle(population[:popn_cutoff])

        #parallel section
        pool = mp.Pool(num_workers)
        args = []
        for w in range(num_workers):
            #allocating work, gives different individuals to each worker
            #num_indivs = survive_percent
            start = int((w*num_survive)%popn_cutoff)
            #stop = int(((w+1)*num_survive)%popn_cutoff)
            #if (stop==0): stop = popn_cutoff

            #not sure if copies are nec
            copy_popn = []
            for p in range(num_survive):
                copy_popn.append(population[start+p].copy())

            #print("population indices: " + str(start) + " to " + str(stop))
            args.append([configs, w, copy_popn, num_return, output_dir])
        pool.starmap(evolve_worker, args)

        print("Workers should be finished, master continuing.")

        population = read_in_workers(num_workers, population, output_dir, num_return)
        pool.close()

    eval_fitness(population, fitness_type)
    output.to_csv(population, output_dir)

    print("Evolution finished, generating images.")
    plot_nets.single_run_plots(output_dir, master_gens, output_freq, pop_size)

    print("Master finished.")


def evolve_worker(configs, worker_ID, founder_population, num_return, output_dir):
    #get configs
    avg_degree = int(configs['average_degree'])
    #output_dir = configs['output_directory'].replace("v4nu_minknap_1X_both_reverse/", '')  #no idea where this is coming from
    grow_freq = float(configs['growth_frequency'])
    pressure = math.ceil ((float(configs['PT_pairs_dict'][1][0])/100.0))
    tolerance = configs['PT_pairs_dict'][1][1]
    pop_size = int(configs['population_size'])
    crossover_freq = float(configs['crossover_frequency'])
    crossover_fraction = float(configs['crossover_percent'])/100
    mutation_freq = float(configs['mutation_frequency'])
    fitness_type = int(configs['fitness_type'])
    mutation_bias = str(configs['mutation_bias'])
    if (mutation_bias == "True"):   mutation_bias = True
    elif (mutation_bias == "False"): mutation_bias = False
    else:   print("Error in configs: mutation_bias should be True or False.")

    survive_percent = int(configs['percent_survive'])
    survive_fraction = float(survive_percent)/100
    num_survive = int(round(pop_size*survive_fraction))
    sampling_rounds = int(configs['sampling_rounds'])
    max_sampling_rounds = int(configs['sampling_rounds_max'])
    knapsack_solver     = cdll.LoadLibrary(configs['KP_solver_binary'])
    start_size = int(configs['starting_size'])

    #new configs
    worker_base_gens = int(configs['worker_base_generations'])

    output_dir += str(worker_ID)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    population = [Net(nx.DiGraph(),i) for i in range(pop_size)] #just blank nets
    for i in range(num_survive):
        population[i] = founder_population[i]

    for g in range(worker_base_gens): #later change to increase worker_base_gen^curr_master_gen

        # breed, ocassionally cross, otherwise just replicates
        if (crossover_freq != 0 and g % int(1 / crossover_freq) == 0):
            cross_fraction = crossover_fraction
        else:
            cross_fraction = 0
        breed(population, num_survive, pop_size, cross_fraction)

        for p in range(pop_size):
            # ocassional growth
            if (grow_freq != 0 and (g % int(1 / grow_freq) == 0)):
                grow(population[p].net, start_size, avg_degree)

            # mutation
            for node in population[p].net.nodes():
                if (random.random() < mutation_freq):
                    mutate(population[p].net, node, mutation_bias)

            # apply pressure
            # assumes all nets are the same size
            num_samples_relative = min(max_sampling_rounds,len(population[0].net.nodes()) * sampling_rounds)
            pressure_relative = int(pressure * len(population[0].net.nodes()))
            population[p].fitness_parts = pressurize(population[p].net, pressure_relative, tolerance, knapsack_solver, fitness_type, num_samples_relative)

        eval_fitness(population, fitness_type)

    write_out_worker(num_return, population, output_dir)

    print("Worker " + str(worker_ID) + " finished.")


def pareto_rank(population):
    #MIN
    n = len(population)
    for i in range(n):
        population[i].fitness = 0

    for i in range(n):
        for j in range(n):
            if (i != j):
                if ((population[i].fitness_parts[0] < population[j].fitness_parts[0] and population[i].fitness_parts[1] <= population[j].fitness_parts[1])
                    or (population[i].fitness_parts[1] < population[j].fitness_parts[1] and population[i].fitness_parts[0] <= population[j].fitness_parts[0])):
                    population[i].fitness += 1

    population.sort(key=operator.attrgetter('fitness'))

def parallel_param_test(configs, testparam_names, testparam_vals):
    #streamlined
    #built for at most FIVE params: testparam_names any length, testparam_vals must be lng 5
    #note that change of population size requires additional manipulation

    if (len(testparam_vals) != 5): print("ERROR in parallel_param_test(): testparam_vals must be length 5, use [0] as a filler.")
    if (len(testparam_names) != 5): print("ERROR in parallel_param_test(): testparam_names must be length 5, use None as a filler.")

    gens = int(configs['generations'])
    crossover_percent = float(configs['crossover_percent'])/100
    mutation_freq = float(configs['mutation_frequency'])
    avg_degree = int(configs['average_degree'])
    output_dir = configs['output_directory'].replace("v4nu_minknap_1X_both_reverse/", '')  #no idea where this is coming from
    grow_freq = float(configs['growth_frequency'])
    output_freq = float(configs['output_frequency'])
    num_workers = int(configs['number_of_workers'])
    pressure = math.ceil ((float(configs['PT_pairs_dict'][1][0])/100.0))
    tolerance = configs['PT_pairs_dict'][1][1]
    start_size = int(configs['starting_size'])
    survive_fraction = float(configs['percent_survive'])/100
    pop_size = int(configs['population_size'])
    num_survive = int(round(pop_size*survive_fraction))
    population = [Net(M.copy(), i) for i in range(pop_size)]
    fitness_hist_freq = 1 #ie no history
    crossover_freq = float(configs['crossover_frequency'])
    fitness_type = int(configs['fitness_type'])

    mutation_bias = str(configs['mutation_bias'])
    if (mutation_bias == "True"):   mutation_bias = True
    elif (mutation_bias == "False"): mutation_bias = False
    else:   print("Error in configs: mutation_bias should be True or False.")


    lng = []
    num_workers = 1 #override configs to match # param sets
    for i in range (len(testparam_vals)):
        lng.append(len(testparam_vals[i]))
        num_workers *= lng[-1]

    param_names = ["num_workers", "gens", "num_survive", "crossover_percent", "crossover_freq", "grow_freq", "mutation_freq",  "mutation_bias", "output_dir",  "pressure", "tolerance", "fitness_hist_freq", "fitness_type", "avg_degree"]
    param_vals = [num_workers, gens, num_survive, crossover_percent, crossover_freq, grow_freq, mutation_freq, mutation_bias, output_dir, pressure, tolerance, fitness_hist_freq, fitness_type, avg_degree]

    output.init_csv(pop_size, num_workers, output_dir, configs)
    worker_configs_file = output_dir + "/worker_configs.csv"
    with open(worker_configs_file, 'w') as outConfigs:
        title = "Worker #"
        for i in range(len(testparam_names)):
            if (testparam_names[i] != None):
                title += "," + str(testparam_names[i])
        title += "\n"
        outConfigs.write(title)


    pool = mp.Pool(num_workers)
    args = []
    for i in range(lng[0]):
        if (testparam_names[0] != None):
            indx = param_names.index(testparam_names[0])
            param_vals[indx] = testparam_vals[0][i]

        for j in range(lng[1]):
            if (testparam_names[1] != None):
                indx = param_names.index(testparam_names[1])
                param_vals[indx] = testparam_vals[1][j]

            for k in range(lng[2]):
                if (testparam_names[2] != None):
                    indx = param_names.index(testparam_names[2])
                    param_vals[indx] = testparam_vals[2][k]

                for l in range(lng[3]):
                    if (testparam_names[3] != None):
                        indx = param_names.index(testparam_names[3])
                        param_vals[indx] = testparam_vals[3][l]

                    for m in range(lng[4]):
                        if (testparam_names[4] != None):
                            indx = param_vals.index(testparam_names[4])
                            param_vals[indx] = testparam_vals[4][m]

                        ID = (i*lng[1]*lng[2]*lng[3]*lng[4]+j*lng[2]**lng[3]*lng[4]+k*lng[3]*lng[4]+l*lng[4]+m)
                        indices = [i,j,k,l,m]
                        #just for file writing
                        with open(worker_configs_file, 'a') as outConfigs:
                            outConfigs.write(str(ID))
                            for n in range(len(testparam_vals)):
                                if (testparam_vals[n] != [0]):
                                    outConfigs.write("," + str(testparam_vals[n][indices[n]]))
                                    #worker_unq_params.append(testparam_vals[n][indices[i]])
                            outConfigs.write("\n")

                        # note that nets are first grown to start_size before passing to workers
                        population_copy = [population[p].copy() for p in range(pop_size)]
                        for p in range(pop_size):
                            grow(population_copy[p].net, start_size, param_vals[11])

                        worker_args = []
                        for n in range(len(param_vals)+3):  #params in evolve_worker()
                            if (n==0): worker_args.append(ID)
                            elif (n==1): worker_args.append(configs)
                            elif (n==2): worker_args.append(population_copy)
                            else: worker_args.append(param_vals[n-3])


                        output.parallel_configs(ID, output_dir, testparam_names, testparam_vals, indices)
                        args.append(worker_args)


    print("Starting parallel parameter search.")
    pool.starmap(evolve_worker_paramtest, args)

    print("Done evolving parameter sets, generating images.")
    plot_nets.param_plots(output_dir, num_workers, gens, output_freq, pop_size, False)

    '''
    plot_nets.features_over_time(output_dir,num_workers,gens,pop_size, output_freq)
    plot_nets.fitness_over_params(output_dir, num_workers)

    print("Drawing degree distribution images.")
    plot_nets.degree_distrib(output_dir,num_workers,gens, output_freq)
    '''

    print("Done.")




# RETIRED PLOTS
#RETIRED FNS(), may be of use as reference
def fitness_over_params(dirr, num_workers, feature_info, titles):

    num_features = len(titles)
    for i in range (num_features):
        x = []
        y = []
        xticks = []
        for w in range(num_workers):
            x.append(w)
            y.append(feature_info[w][i])
            xticks.append(w)
        plt.bar(x,y, align="center")
        plt.xticks(xticks)
        plt.title(titles[i])
        plt.xlabel("Parameter Set")
        plt.ylabel("Feature Value at Final Generation")
        plt.savefig(dirr + "/param_images/" + str(titles[i]) + ".png")
        plt.clf()

def write_outro (dirr, num_workers, gens, num_indivs, output_freq, worker_info, titles):
    #incld how to find max,min of param test

    num_features = len(titles)
    mins = [100000 for i in range(num_features)]
    maxs = [0 for i in range(num_features)]
    endpts = [[0 for i in range(num_features)] for j in range(num_workers)]

    with open(dirr + "/outro_info.csv", 'w') as outro_file:
        output = csv.writer(outro_file)

        header = ["Param Set #"]
        for i in range(num_features):
            header += ["Min" + str(titles[i])]
            header += ["Max" + str(titles[i])]
            header += ["Endpoint" + str(titles[i])]

        output.writerow(header)

        for w in range(num_workers):
            row = []
            row.append(w)
            for i in range(0,num_features):
                vals = []
                feature_endpts = []
                for j in range(num_indivs):
                    for g in range(int(gens*output_freq)):
                        vals.append(worker_info[w,g,j,i]) #titles are one off since net size not included
                    feature_endpts.append(worker_info[w,int(gens*output_freq)-1,j,i])
                minn = min(vals)
                maxx = max(vals)
                endpt = max(feature_endpts)
                endpts[w][i] = endpt
                row.append(minn)
                row.append(maxx)
                row.append(endpt)
                mins[i] = min(minn, mins[i])
                maxs[i] = max(maxx, maxs[i])
            output.writerow(row)

    return mins, maxs, endpts



def old_fitness_defs():
    # for reference from prev runs

    '''
    if (fitness_type == 0 or fitness_type == 1 or fitness_type == 2):
        return [RGGR, ETB, ben_ratio]
    elif (fitness_type == 3 or fitness_type == 4 or fitness_type == 5):
        return [RGAllR, ETB, ben_ratio]
    elif (fitness_type == 6 or fitness_type == 7 or fitness_type == 8):
        return [RGGR, dist_in_sack, ben_ratio]
    elif (fitness_type == 9 or fitness_type == 10 or fitness_type == 11):
        return [RGAllR, dist_in_sack, ben_ratio]
    elif (fitness_type == 12 or fitness_type == 13 or fitness_type == 14): #doesn't work at all
        node_to_edge_ratio = num_nodes/ num_edges
        return [node_to_edge_ratio, dist_in_sack, ben_ratio]
    elif (fitness_type == 15):
        return [RGAllR, ETB, ben_ratio]
    elif (fitness_type == 16):
        return [RGAllR, ETB, dist_in_sack]
    elif (fitness_type == 17):
        return [RGAllR, ETB, RGAllR*ETB]
    elif (fitness_type == 18):
        return [RGAllR, ETB, math.pow(ETB,RGAllR)]
    elif (fitness_type == 19):
        return [RGAllR, ETB, ben_ratio*ETB]
    elif (fitness_type == 20):
        return [RGAllR, ETB, ratiodist]
    elif (fitness_type == 21):
        return [RGAllR, ETB, ben_ratio/soln_size]
    elif (fitness_type == 22):
        return [RGAllR, ETB, ben_ratio*RGAllR]
    '''
    return



def orig_pref():
    ''' ORIG
            if (pref_type == 0):
            edge = rd.sample(net.edges(), 1)
            edge = edge[0]
            # assumes undirected implm
            from_edges = len(net.out_edges(edge[0]) + net.in_edges(edge[0]))
            to_edges = len(net.out_edges(edge[1]) + net.in_edges(edge[1]))
            if (rd.random() < from_edges / (from_edges + to_edges)):
                node = edge[0]
            else:
                node = edge[1]

            pre_size = post_size = len(net.edges())
            while (pre_size == post_size):  # ensure that net adds
                node2 = node
                while (node2 == node):
                    node2 = rd.sample(net.nodes(), 1)
                    node2 = node2[0]
                sign = rd.randint(0, 1)
                if (sign == 0):     sign = -1
                if (rd.random() < .5):
                    net.add_edge(node, node2, sign=sign)
                else:
                    net.add_edge(node2, node, sign=sign)
                post_size = len(net.edges())
    '''
    return