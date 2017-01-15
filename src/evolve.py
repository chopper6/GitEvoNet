#!/usr/bin/python3
import math, operator, os, random, sys, csv
from ctypes import cdll
import multiprocessing as mp
import networkx as nx
from time import process_time as ptime
import time

os.environ['lib'] = "/home/2014/choppe1/Documents/EvoNet/virt_workspace/lib"
sys.path.insert(0, os.getenv('lib'))
import util, init, solver, reducer
import output, plot_nets


class Net:
    def __init__(self, net, id):
        self.fitness = 0    #aim to max
        self.fitness_parts = [0]*2   #leaf-fitness, hub-fitness
        self.net = net.copy()
        self.id = id  #irrelv i think

    def copy(self):
        copy = Net(self.net, self.id)
        copy.fitness = self.fitness
        copy.fitness_parts = self.fitness_parts
        assert (copy != self)
        return copy


# EVO CONTROL FN'S

def evolve_master(configs):
    #get configs
    num_workers = int(configs['number_of_workers'])
    output_dir = configs['output_directory'].replace("v4nu_minknap_1X_both_reverse/", '')  #no idea where this is coming from
    crossover_freq = float(configs['crossover_frequency'])
    crossover_fraction = float(configs['crossover_percent'])/100
    fitness_type = int(configs['fitness_type'])
    survive_percent = int(configs['percent_survive'])
    survive_fraction = float(survive_percent)/100
    avg_degree = int(configs['average_degree'])
    grow_freq = float(configs['growth_frequency'])
    output_freq = float(configs['output_frequency'])

    #new configs
    base_gens = int(configs['base_generations'])
    init_type = int(configs['initial_net_type'])
    #nodes_per_worker = int(configs['nodes_per_worker'])
    start_size = int(configs['starting_size'])
    end_size = int(configs['ending_size'])
    pop_size = int(configs['population_size'])
    num_survive = int(round(pop_size * survive_fraction))
    #nets_per_worker = int(math.ceil(pop_size / num_workers))
    gen_slowdowns = int(configs['generation_slowdowns'])

    #output_pref
    init_dirs(num_workers, output_dir)
    output.init_csv(output_dir, configs)

    pop_size = 40 * num_workers #same eqn as DYNAM POPN SIZE, later add to configs
    population = gen_init_population(init_type, start_size, pop_size)
    eval_fitness(population, fitness_type)

    size = start_size
    size_iters=0
    while (size < end_size):

        t0 = ptime()
        if (size_iters % int(1 / output_freq) == 0):
            output.to_csv(population, output_dir)

        percent_size = float(size-start_size)/float(end_size-start_size)

        #dynam popn size
        #pop_size = num_workers
        worker_pop_size = math.ceil(10*math.pow(math.e,-4*percent_size))
        pop_size = worker_pop_size*num_workers
        num_survive = int(pop_size / num_workers)
        if (num_survive < 1): 
            num_survive = 1
            print("WARNING evo_master(): num_survive goes below 1, set to 1 instead")
        
        #dynam gens
        gens_per_growth = math.ceil(math.pow(math.e, 4*percent_size))
        worker_gens = worker_pop_size
        master_gens = math.ceil(gens_per_growth/worker_gens)

        print("At size " + str(size) + "=" + str(len(population[0].net.nodes())) + ",\tnets per worker = " + str(worker_pop_size) + ",\tpopn size = " + str(pop_size) + ",\tnum survive = " + str(num_survive) + ",\tdynam gens = " + str(gens_per_growth) + ",\tworker gens = " + str(worker_gens) + ",\tmaster gens = " + str(master_gens))
        t1 = ptime()
        init_time = t1-t0
        distrib, minions, readd = 0,0,0

        for g in range(master_gens):
            # curr no breeding, just replicates
            '''
            if (crossover_freq != 0 and g % int(1 / crossover_freq) == 0):   cross_fraction = crossover_fraction
            else:                                                            cross_fraction = 0
            population = breed(survivors, pop_size, cross_fraction)
            '''

            t0 = ptime()
            pool = mp.Pool(num_workers)
            args = []

            # check that population is unique
            for p in range(pop_size):
                for q in range(0, p):
                    if (p != q): assert (population[p] != population[q])

            #DISTRIBUTE WORKERS
            for w in range(num_workers):
                #distrib of popn not quite generalizable, nets_per_worker should relate to num_survive
                #or at least should ensure that ONLY top nets are being passed
                sub_pop = [population[p].copy() for p in range(num_survive)]  #population[p] should NOT be shared, ie each worker should be working on its own COPY
                worker_args = [w, sub_pop, worker_gens, g, gens_per_growth, num_survive, master_gens, configs]
                args.append(worker_args)
            t1 = ptime()
            distrib += t1-t0

            t0 = ptime()
            worker_population = pool.starmap(evolve_minion, args)
            pool.close()
            pool.join()

            del population

            t1 = ptime()
            minions += t1-t0

            t0 = ptime()
            #params instead of files seem marginally faster
            population = parse_worker_popn(worker_population, num_survive)
            #population = read_in_workers(num_workers, output_dir, num_survive)
            #only replaces num_survive in population, returns sorted
            t1 = ptime()
            readd += t1-t0

        size = len(population[0].net.nodes())
        size_iters+=1
        '''
        print("init took " + str(init_time) + " secs.")
        print("distrib workers took " + str(distrib) + " secs.")
        print("minions took " + str(minions) + " secs.")
        print("reading in workers took " + str(readd) + " secs.\n")
        '''
    output.to_csv(population, output_dir)

    print("Evolution finished, generating images.")
    plot_nets.single_run_plots(output_dir)

    print("Master finished.")

def evolve_minion(worker_ID, population, worker_gens, curr_master_gen, gens_per_growth, num_survive, master_gens, configs):
    #retrieve configs
    t0 = ptime()
    pressure = math.ceil ((float(configs['PT_pairs_dict'][1][0])/100.0))
    tolerance = configs['PT_pairs_dict'][1][1]
    mutation_freq = float(configs['mutation_frequency'])
    sampling_rounds = int(configs['sampling_rounds'])
    max_sampling_rounds = int(configs['sampling_rounds_max'])
    knapsack_solver = cdll.LoadLibrary(configs['KP_solver_binary'])
    fitness_type = int(configs['fitness_type'])

    mutation_bias = str(configs['mutation_bias'])
    if (mutation_bias == "True"):   mutation_bias = True
    elif (mutation_bias == "False"): mutation_bias = False
    else:   print("Error in configs: mutation_bias should be True or False.")

    survive_percent = int(configs['percent_survive'])
    survive_fraction = float(survive_percent)/100
    worker_num_survive = math.ceil(len(population)*survive_fraction)

    output_dir = configs['output_directory'].replace("v4nu_minknap_1X_both_reverse/", '')
    output_dir += str(worker_ID)

    pop_size = num_survive #for current build
    t1 = ptime()
    init_t = t1-t0
    growth_t, mutate_t, pressure_t, eval_t, replic_t = 0,0,0,0,0
    num_growth = 0

    for g in range(worker_gens):
        #worker replication
        t0=ptime()
        if (g != 0):
            for p in range(worker_num_survive,pop_size):
                population[p] = population[p%worker_num_survive].copy()
                assert (population[p] != population[p%worker_num_survive])
        t1=ptime()
        replic_t += t1-t0

        if (worker_ID == 0): print ("Minion population fitness: " + population[p].fitness for p in range(pop_size))

        #check that population is unique
        for p in range(pop_size):
            for q in range(0,p):
                if (p != q): assert (population[p] != population[q])

        for p in range(pop_size):
            t0 = ptime()
            if ((curr_master_gen+g) % gens_per_growth  == 0):
                grow(population[p].net, 1)
                num_growth += 1
            t1 = ptime()
            growth_t += t1-t0

            # mutation
            t0=ptime()
            for node in population[p].net.nodes():
                if (random.random() < mutation_freq):
                    mutate(population[p].net, node, mutation_bias)
            t1=ptime()
            mutate_t += t1-t0
            # apply pressure
            # assumes all nets are the same size
            t0 = ptime()
            num_samples_relative = min(max_sampling_rounds, len(population[0].net.nodes()) * sampling_rounds)
            pressure_relative = int(pressure * len(population[0].net.nodes()))
            population[p].fitness_parts = pressurize(configs, population[p].net, pressure_relative, tolerance, knapsack_solver,fitness_type, num_samples_relative)
            t1 = ptime()
            pressure_t += t1-t0
            '''
            if (len(population[p].net.nodes()) > len(population[p].net.edges())):
                print("ERROR in minion: too many nodes")
            elif (2*len(population[p].net.nodes()) < len(population[p].net.edges())):
                print("ERROR in minion: too many edges")
            '''
        t0=ptime()
        eval_fitness(population, fitness_type)
        t1=ptime()
        eval_t+=t1-t0

    t0=ptime()
    write_out_worker(worker_ID, population, num_survive, output_dir)
    t1=ptime()
    write_t = t1-t0

    if (worker_ID == 0 and curr_master_gen==0):
        '''
        print("\nminion init took " + str(init_t) + " sec.")
        print("minion replication took " + str(replic_t) + " sec.")
        print("minion growth took " + str(growth_t) + " sec.")
        print("minion mutate took " + str(mutate_t) + " sec.")
        print("minion pressurize took " + str(pressure_t) + " sec.")
        print("minion eval fitness took " + str(eval_t) + " sec.")
        print("minion write took " + str(write_t) + " sec.\n")
        '''
        orig_dir = configs['output_directory'].replace("v4nu_minknap_1X_both_reverse/", '')
        end_size = len(population[0].net.nodes())
        output.minion_csv(orig_dir, pressure_t, master_gens, num_growth, end_size)

    return population

# GRAPH FN'S
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

# EVO OPERATION FN'S
def breed(survivors, pop_size, cross_fraction):
    #duplicate or cross
    #could pref fitter survivors, but so few survive that doesn't seem signif
    population = [Net(nx.DiGraph(),i) for i in range(pop_size)]
    num_survive = len(survivors)

    for p in range(num_survive):
        population[p] = survivors[p]

    #reproduction, crossover
    for p in range(num_survive, pop_size):

        if (p + num_survive < pop_size*cross_fraction): #sexual
            rand1 = random.randint(0,num_survive-1)
            rand2 = random.randint(0, num_survive-1)
            while (rand1==rand2):
                rand2 = random.randint(0, num_survive-1)
            population[p].net = cross_bfs(population[rand1].net, population[rand2].net)

        else:   #asexual
            rand = random.randint(0,num_survive-1)
            population[p].net = population[rand].net.copy()

    return population


def cross_bfs(parent1, parent2):
    #passes and returns nets

    #if ((len(parent1.nodes())) != (len(parent2.nodes()))): print("WARNING: two crossing parents don't have same # nodes!" + str((len(parent1.nodes()))) + str(len(parent2.nodes())))
    size1 = random.randint(0,len(parent1.nodes())-1)
    size2 = len(parent2.nodes())-size1

    #if (len(list(nx.weakly_connected_component_subgraphs(parent1))) != 1): print("unconnected parent!")

    node1 = random.SystemRandom().sample(parent1.nodes(),1)
    node2 = random.SystemRandom().sample(parent2.nodes(),1)

    #PARENT1
    #mem ineff implementation
    edges = parent1.edges(data=True)
    edges1 = [[[None for k in range(3)] for i in range(len(edges)+1)] for j in range(len(edges)+1)]
    for edge in edges:
        i = min(edge[0],edge[1])
        j = max(edge[0],edge[1])
        edges1[i][j] = edge[0], edge[1], edge[2]['sign']

    bfs1 = nx.bfs_edges(parent1.to_undirected(), node1[0])
    component1 = nx.DiGraph()

    while len(component1.nodes()) < size1:
        edge_undir = next(bfs1)
        i = min(edge_undir[0], edge_undir[1])
        j = max(edge_undir[0], edge_undir[1])
        component1.add_edge(edges1[i][j][0], edges1[i][j][1], sign=edges1[i][j][2])

    #PARENT2
    edges = parent2.edges(data=True)
    edges2 = [[[None for k in range(3)] for i in range(len(edges)+1)] for j in range(len(edges)+1)]
    for edge in edges:
        i = min(edge[0],edge[1])
        j = max(edge[0],edge[1])
        edges2[i][j] = edge[0], edge[1], edge[2]['sign']

    bfs2 = nx.bfs_edges(parent2.to_undirected(), node2[0])
    component2 = nx.DiGraph()

    while len(component2.nodes()) < size2:
        edge_undir = next(bfs2)
        i = min(edge_undir[0], edge_undir[1])
        j = max(edge_undir[0], edge_undir[1])
        component2.add_edge(edges2[i][j][0], edges2[i][j][1], sign=edges2[i][j][2])

    #if (size1 != len(component1.nodes()) or size2 != len(component2.nodes())): print("ERROR: incorr # parent nodes")

    #print("PARENT EDGES: " + str(component1.edges()) + "PARENT2: "  +  str(component2.edges()))

    child = nx.disjoint_union(component1, component2)
    #print(len(child.nodes()))
    #print("CHILLE edges : " + str(child.edges()))
    #if (len(child.nodes()) > 2+len(parent1.nodes())): print("WARNING: resulting child is different > size of parent + 2.")
    #if (len(list(nx.weakly_connected_component_subgraphs(child))) != 2): print("WARNING: child is not 2 components, but " + str(len(list(nx.weakly_connected_component_subgraphs(child)))) + " instead.")

    connect_components(child)

    return child


def cross_aln(parent1, parent2, cross_type):
    #only ops on out edges of selected nodes
    #laer: try bfs and dfs in addtn to rand
    if (len(list(nx.weakly_connected_component_subgraphs(parent1))) != 1): print("unconnected parent!")

    size1 = random.randint(0,len(parent1.nodes())-1)
    swap_nodes = random.SystemRandom().sample(parent1.nodes(),size1)

    for swap_node in swap_nodes:
        for edge in parent2.out_edges(swap_node):
            parent2.remove_edge(edge[0], edge[1])
        for edge in parent1.out_edges(swap_node):
            parent1.add_edge(edge[0], edge[1])


def eval_fitness(population, fitness_type):
    #determines fitness of each individual and orders the population by fitness

    if (fitness_type % 3 == 0):
        generic_rank(population)

    else:
        for p in range(len(population)):
            if (fitness_type % 3 == 1):
                population[p].fitness = population[p].fitness_parts[0] * population[p].fitness_parts[1]
            else:
                population[p].fitness = math.pow(population[p].fitness_parts[1],population[p].fitness_parts[0])

    population = sorted(population,key=operator.attrgetter('fitness'), reverse=True)
    #reverse since MAX fitness function


def gen_init_population(init_type, start_size, pop_size):
    #LATER: diff init types corresp to diff starting positions

    if (init_type == 0):
        population = [Net(nx.DiGraph(), i) for i in range(pop_size)]
        for p in range(pop_size):
            while (len(population[p].net.nodes()) < start_size): grow(population[p].net, 1)

    elif (init_type == 1):
        population = [Net(nx.erdos_renyi_graph(200,.01, directed=True, seed=None), i) for i in range(pop_size)]
        for p in range(pop_size):
            edge_list = population[p].net.edges()
            for edge in edge_list:
                sign = random.randint(0, 1)
                if (sign == 0):     sign = -1
                population[p].net[edge[0]][edge[1]]['sign'] = sign

    else:
        print("ERROR in gen_init_population(): unknown init_type.")
        return

    '''
    for p in range(pop_size):
        while (len(population[p].net.nodes()) > len(population[p].net.edges())):
            if (init_type == 1):
                print("WARNING in gen_init_popn: eR graph should not need further initialization.")
            net = population[p].net
            #add edge
            node = random.SystemRandom().sample(net.nodes(), 1)
            node = node[0]
            node2 = node
            while (node2 == node):
                node2 = random.SystemRandom().sample(net.nodes(), 1)
                node2 = node2[0]
            sign = random.randint(0, 1)
            if (sign == 0):     sign = -1
            net.add_edge(node, node2, sign=sign)
    '''
    return population

def generic_rank(population):

    for p in range(len(population)):
        population[p].fitness = 0

    for i in range(2): #leaf and hub features
        for p in range(len(population)):
            population[p].id = population[p].fitness_parts[i]
        population.sort(key=operator.attrgetter('id'))
        #no reverse, ie MIN features, to MAX fitness consistent with other definitions
        for p in range(len(population)):
            population[p].fitness += p



def grow(net, avg_degree):
    #operates only on nodes
    #adds edges to or from a new node
    # add numbered node
    node = len(net.nodes())
    net.add_node(node)

    if (len(net.nodes()) >= 2): #if size 1 would add an extra node

        for i in range(avg_degree):
            prev_num_edges = post_num_edges = len(net.edges())
            while (prev_num_edges == post_num_edges):
                node2 = node
                while (node2 == node):
                    node2 = random.randint(0, len(net.nodes()) - 1)
                    sign = random.randint(0, 1)
                    if (sign == 0):     sign = -1

                direction = random.random()             #rand in or out
                if (direction < .5):
                    net.add_edge(node2, node, sign=sign)
                else:
                    net.add_edge(node, node2, sign=sign)

                post_num_edges = len(net.edges())
    #ASSUMPTION: net sh uld remain connected
    #connect_components
    #shouldn't disconnect, remove if doesn't appear as issue
    components = list(nx.weakly_connected_component_subgraphs(net))
    #if (len(components) != 1): print("ERROR in grow(): graph is not connected.")

def mutate(net, node, bias):
    #operates on edges of given node
    #bias is boolean and prefs adding edges to nodes with high degree and vice versa

    # mutation options: rm edge, add edge, change edge target, change edge sign, reverse edge direction

    mut_type = random.random()
    num_nodes = len(net.nodes())
    num_edges = len(net.edges())

    #temp rm boundary
    rm_allowed = True
    add_allowed = True
    '''
    if (num_nodes == num_edges): rm_allowed = False
    else: rm_allowed = True
    if (2*num_nodes == num_edges): add_allowed = False
    else: add_allowed = True
    '''
    #handle no out edges case, only chance of adding
    if (len(net.out_edges(node)) == 0 and add_allowed == True):
        if (mut_type < .4):
            node2 = node
            while (node2 == node):
                node2 = random.SystemRandom().sample(net.nodes(), 1)
                node2 = node2[0]
            sign = random.randint(0, 1)
            if (sign == 0):     sign = -1
            net.add_edge(node, node2, sign=sign)
    
    elif (len(net.out_edges(node)) != 0):
 
        if (mut_type < .4):  #add or rm
            if (bias == True):
                ngh_deg = nx.average_neighbor_degree(net,nodes=[node])
                ngh_deg = ngh_deg[node]
                if (ngh_deg != 0):
                    add_prob = (net.degree(node))/(ngh_deg+net.degree(node))
                else: add_prob = .5
            else:   add_prob = .5
    
            if (random.random() < add_prob):
                # add edge
                if (add_allowed == True):
                    pre_edges = post_edges = len(net.edges())
                    while (pre_edges == post_edges):
                        node2 = node
                        while (node2 == node): 
                            node2 = random.SystemRandom().sample(net.nodes(), 1)
                            node2 = node2[0]
                        sign = random.randint(0, 1)
                        if (sign == 0):     sign = -1
                        net.add_edge(node, node2, sign=sign)
                        post_edges = len(net.edges())    

            else:
                # rm edge
                if (rm_allowed == True):
                    edge = random.SystemRandom().sample(net.out_edges(node), 1)
                    edge = edge[0]
                    net.remove_edge(edge[0], edge[1])
    
                    # ASSUMPTION: net should remain connected
                    #while (not nx.is_weakly_connected(net)): connect_components(net)
    
        elif(mut_type < .6):
            #rewire: change an edge node
            pre_edges = post_edges = len(net.edges())
            edge = random.SystemRandom().sample(net.out_edges(node), 1)
            edge = edge[0]
            net.remove_edge(edge[0], edge[1])
            node2 = node
            while (node2 == node):
                node2 = random.SystemRandom().sample(net.nodes(), 1)
                node2 = node2[0]
            sign = random.randint(0, 1)
            if (sign == 0):     sign = -1
            net.add_edge(node, node2, sign=sign)
            
            post_edges = len(net.edges())
            while(pre_edges != post_edges): #last add_edge failed, add a random one
                node2 = node
                while (node2 == node):
                    node2 = random.SystemRandom().sample(net.nodes(), 1)
                    node2 = node2[0]
                sign = random.randint(0, 1)
                if (sign == 0):     sign = -1
                net.add_edge(node, node2, sign=sign)
                post_edges = len(net.edges())

            # ASSUMPTION: net should remain connected
            #while (not nx.is_weakly_connected(net)): connect_components(net)
            #if (len(net.nodes()) > len(net.edges())):
                #print("ERROR post mutn() rewire: too many nodes")
        
        elif (mut_type < .8):
            #change direction of edge
            pre_edges = post_edges = len(net.edges())
            edge = random.SystemRandom().sample(net.out_edges(node), 1)
            edge = edge[0]
            sign = net[edge[0]][edge[1]]['sign']
            net.remove_edge(edge[0], edge[1])
            net.add_edge(edge[1], edge[0], sign=sign)

            post_edges = len(net.edges())
            while(pre_edges != post_edges): #last add_edge failed, add a random one
                node2 = node
                while (node2 == node):
                    node2 = random.SystemRandom().sample(net.nodes(), 1)
                    node2 = node2[0]
                sign = random.randint(0, 1)
                if (sign == 0):     sign = -1
                net.add_edge(node, node2, sign=sign)
                post_edges = len(net.edges()) 
        else:
            #change edge sign
            pre_edges = len(net.edges())
            edge = random.SystemRandom().sample(net.out_edges(node), 1)
            edge = edge[0]
            net[edge[0]][edge[1]]['sign'] = -1*net[edge[0]][edge[1]]['sign']
            post_edges = len(net.edges())
            if (pre_edges != post_edges): print("ERROR: mutn sign change has changed the number of edges!")

def parse_worker_popn (worker_population, num_survive):
    population = []
    for worker in worker_population:
        for indiv in worker:
            population.append(indiv)
    population.sort(key=operator.attrgetter('fitness'))
    # population.reverse() #MAX fitness function
    # creating something new that is sorted vs sorting in place
    # should be same as
    population = sorted(population,key=operator.attrgetter('fitness'), reverse=True)

    return population[:num_survive]


def pressurize(configs, net, pressure_relative, tolerance, knapsack_solver, fitness_type, num_samples_relative):
    #does all the reducing to kp and solving
    #how can it call configs without being passed???
    fitness_fun = configs['fitness_fun']
    RGGR, ETB = 0, 0
    dist_in_sack = 0
    dist_sq_in_sack = 0

    ETB_ratio = 0
    RGAllR = 0

    kp_instances = reducer.reverse_reduction(net, pressure_relative, int(tolerance), num_samples_relative, configs['advice_upon'], configs['biased'], configs['BD_criteria'])

    for kp in kp_instances:
        a_result = solver.solve_knapsack(kp, knapsack_solver)

        #various characteristics of a result
        instance_RGGR, instance_ETB,inst_dist_in_sack, inst_dist_sq_in_sack, inst_ETB_ratio, inst_RGAllR  = 0,0,0,0,0,0

        # the solver returns the following as a list:
        # 0		GENES_in: 		a list, each element in the list is a tuple of three elements: node(gene) ID, its value(benefit), its weight(damage)
        # 1     number_green_genes
        # 2     number_red_genes
        # 3     number_grey genes

        # before the solver would return
        # 0		TOTAL_Bin:		total value of objects inside the knapsack,
        # 1		TOTAL_Din:		total weight of objects inside the knapsack
        # 2		TOTAL_Bout:		total value of objects outside knapsack
        # 3		TOTAL_Dout:		total weight of object outside knapsack,
        # 4		GENES_in: 		a list, each element in the list is a tuple of three elements: node(gene) ID, its value(benefit), its weight(damage)
        # 5		GENES_out:		a list of tuples also, as above, with genes that are outside the knapsack
        # 6		green_genes:	a list of tuples also, as above, with genes that have values greater than zero but zero weights (hence they are automatically inside the knaspack and not included in the optimization)
        # 7		red_genes:		a list of tuples also, as above, with genes that have weights greater than zero but zero values (hence they are automatically outside the knaspack and not included in the optimization)
        # 8		grey_genes:		a list of tuples also, as above, with genes that have greater than zero values and weights (these are the nodes that were optimized over to see which should be in and which should be out)
        # 9		coresize: 		ignore
        # 10	execution_time: in seconds

        if len(a_result) > 0:
            Gs, Bs, Ds, Xs = [], [], [], []
            # -------------------------------------------------------------------------------------------------
            #GENES_in, GENES_out, coresize, execution_time = a_result[4], a_result[5], a_result[9], a_result[10]

            GENES_in, num_green, num_red, num_grey = a_result[0], a_result[1], a_result[2], a_result[3]
            # -------------------------------------------------------------------------------------------------
            soln_bens = []
            for g in GENES_in:

                # g[0] gene name
                # g[1] benefits
                # g[2] damages
                # g[3] if in knapsack (binary)

                #hub score eval pt1
                inst_dist_in_sack += abs(g[1] - g[2])
                inst_dist_sq_in_sack += math.pow((g[1] - g[2]), 2)
                soln_bens.append(g[1])

            #hub score eval pt2
            instance_ETB = sum(set(soln_bens))
            if (sum(soln_bens) != 0): inst_ETB_ratio = sum(set(soln_bens))/sum(soln_bens)
            else: inst_ETB_ratio = sum(set(soln_bens))

            #leaf score eval
            if (num_grey != 0):
                instance_RGGR = (num_green + num_red) / num_grey
            else:
                instance_RGGR = (num_green + num_red)
            inst_RGAllR = (num_green + num_red) / (num_green + num_red + num_grey)

        else:
            print ("WARNING in pressurize(): no results from oracle advice")

        ETB += instance_ETB
        RGGR += instance_RGGR
        dist_in_sack += inst_dist_in_sack
        dist_sq_in_sack += inst_dist_sq_in_sack
        ETB_ratio += inst_ETB_ratio
        RGAllR += inst_RGAllR

    ETB /= num_samples_relative
    RGGR /= num_samples_relative
    dist_in_sack /= num_samples_relative
    dist_sq_in_sack /= num_samples_relative
    ETB_ratio /= num_samples_relative
    RGAllR /= num_samples_relative

    if (fitness_type == 0 or fitness_type == 1 or fitness_type == 2):
        return [RGGR, ETB]
    elif (fitness_type == 3 or fitness_type == 4 or fitness_type == 5):
        return [RGAllR, ETB]
    elif (fitness_type == 6 or fitness_type == 7 or fitness_type == 8):
        return [RGGR, dist_in_sack]
    elif (fitness_type == 9 or fitness_type == 10 or fitness_type == 11):
        return [RGAllR, dist_in_sack]
    elif (fitness_type == 12 or fitness_type == 13 or fitness_type == 14): #doesn't work at all
        node_to_edge_ratio = len(net.nodes())/len(net.edges())
        return [node_to_edge_ratio, dist_in_sack]
    else: print("ERROR in pressurize(): unknown fitness type.")

#INTERNAL IO FUNCTIONS
def init_dirs(num_workers, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for w in range(num_workers):
        dirr = output_dir + "/" + str(w)
        if not os.path.exists(dirr):
            os.makedirs(dirr)
        net_dirr = dirr + "/net"
        if not os.path.exists(net_dirr):
            os.makedirs(net_dirr)
        chars_dirr = dirr + "/net_chars"
        if not os.path.exists(chars_dirr):
            os.makedirs(chars_dirr)

def read_in_workers(num_workers, output_dir, num_survive):
    sub_pop_size = num_survive #for current implementation
    population = [Net(nx.DiGraph(), 0) for i in range(num_survive*num_workers)]
    for w in range(num_workers):
        for p in range(sub_pop_size):
            char_file = output_dir + str(w) + "/net_chars/" + str(p) + ".csv"
            with open(char_file, 'r') as net_char_file:
                chars = net_char_file.readline().split(",")
                population[w * sub_pop_size + p].fitness = float(chars[0])
                population[w * sub_pop_size + p].fitness_parts[0] = float(chars[1])
                population[w * sub_pop_size + p].fitness_parts[1] = float(chars[2])
                population[w * sub_pop_size + p].id = str(chars[3])

    population.sort(key=operator.attrgetter('fitness'))
    population.reverse() #MAX fitness function

    for p in range(num_survive):
        net_file = output_dir + str(population[p].id)
        population[p].net = nx.read_edgelist(net_file, nodetype=int, create_using=nx.DiGraph())

    return population[:num_survive]

def write_out_worker(worker_ID, population, num_survive, output_dir):
    # write top nets to file
    # then write fitness_parts to a csv in same order as net files
    for p in range(num_survive):
        netfile = output_dir + "/net/" + str(p) + ".txt"
        with open(netfile, 'wb') as net_out:
            nx.write_edgelist(population[p].net, net_out)
        netfile = output_dir + "/net_chars/" + str(p) + ".csv"
        population[p].id = str(str(worker_ID) + "/net/" + str(p) + ".txt")
        with open(netfile, 'w') as chars_out:
            #fitness, fitness_parts, id
            chars_out.write(str(population[p].fitness) + "," + str(population[p].fitness_parts[0]) + "," + str(population[p].fitness_parts[1]) + "," + str(population[p].id))



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


if __name__ == "__main__":

    config_file         = util.getCommandLineArgs ()
    M, configs          = init.initialize_master (config_file, 0)

    evolve_master(configs)

    ''' old param test:
    test_names = ["fitness_type", "mutation_freq", "crossover_freq", None, None]
    test_vals = [[11,13],[0,.001],[.1,1],[0],[0]]
    #must match: ["num_workers, gens, num_survive, crossover_percent, mutation_freq, output_dir,  pressure, tolerance, grow_freq"]

    parallel_param_test(configs, test_names, test_vals)
    '''




