#!/usr/bin/python3
import math, operator, os, random, sys, csv
from ctypes import cdll
import multiprocessing as mp
import networkx as nx

os.environ['lib'] = "/Users/Crbn/Desktop/McG Fall '16/EvoNets/evoNet/work_space/lib"
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
        return copy


# GRAPH FN'S
def add_edge(net):  #unused i think
    if (len(net.nodes()) < 2):
        print("ERROR add_edge(): cannot add edge to net with < 2 nodes")
        return -1
    node1 = random.sample(net.nodes(), 1)
    node2 = random.sample(net.nodes(), 1)
    while (node1 == node2):                             #poss infinite loop?
        node2 = random.sample(net.nodes(),1)
    sign = random.randint(0, 1)
    if (sign == 0):     sign = -1
    #if (node1 not in net.nodes() or node2 not in net.nodes()) :
    net.add_edge(node1[0], node2[0], sign=sign)

def connect_components(net):
    #finds connected components and connects 'em
    components = list(nx.weakly_connected_component_subgraphs(net))
    while  (len(components) != 1):
        for i in range(len(components)-1):
            #might be faster method than SystemRandom
            node1 = random.SystemRandom().sample(components[i].nodes(), 1)
            node2 = random.SystemRandom().sample(components[i+1].nodes(), 1)
            if (node1 == node2): print("WARNING connect_components(): somehow same node is picked btwn two diff components.")
            sign = random.randint(0, 1)
            if (sign == 0):     sign = -1
            net.add_edge(node1[0], node2[0], sign=sign)
        components = list(nx.weakly_connected_component_subgraphs(net))

# EVO FN'S
def breed(population, num_survive, pop_size, cross_fraction):
    #duplicate or cross

    #reproduction, crossover
    for p in range(num_survive, pop_size):
        #if (len(list(nx.weakly_connected_component_subgraphs(population[p].net))) != 1): print("WARNING from breed(): unconnected network found")

        repro_type = random.random()
        if (p + num_survive < pop_size*cross_fraction): #sexual
            rand1 = random.randint(0,num_survive-1)
            rand2 = random.randint(0, num_survive-1)
            while (rand1==rand2):
                rand2 = random.randint(0, num_survive-1)
            population[p].net = cross_bfs(population[rand1].net, population[rand2].net)

        else:   #asexual
            rand = random.randint(0,num_survive-1)           #check that gives right range
            population[p].net = population[rand].net.copy()


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

    for p in range(len(population)):
        if (fitness_type % 2 == 0):
            population[p].fitness = population[p].fitness_parts[0] + population[p].fitness_parts[1]
        else:
            population[p].fitness = population[p].fitness_parts[0] * population[p].fitness_parts[1]
    population.sort(key=operator.attrgetter('fitness'))
    population.reverse() #MAX fitness function


def evolve_worker_paramtest(worker_ID,  configs, founder_pop, num_workers, gens, num_survive, crossover_fraction, cross_freq, grow_freq, mut_freq, mut_bias, output_dir, pressure, tolerance, fitness_hist_freq, fitness_type, avg_degree):
    #have to pass a lot more params for: breed, pressurize
    #any params NOT param tested are just init inside of this function

    print("Worker " + str(worker_ID) + " starting.")

    knapsack_solver     = cdll.LoadLibrary(configs['KP_solver_binary'])
    output_freq = float(configs['output_frequency'])
    start_size = int(configs['starting_size'])

    founder_size = len(founder_pop)
    output_dir += str(worker_ID)

    if (founder_size < num_survive):
        print("WARNING in evolve_worker(): more than founder population used for initial breeding.")
        #doesn't entirely break algo, so allowed to continue

    population = founder_pop
    pop_size = founder_size

    max_feature1, max_feature2 = 0, 0

    for g in range(gens):

        if (g == 0 or g % int(1 / output_freq) == 0):
            #popn_info = [len(population[0].net.nodes()), max_feature1, max_feature2]
            output.to_csv(population, output_dir)

        for p in range(pop_size):

            if (grow_freq !=0 and (g==0 or g % int(1/grow_freq) == 0)): #grow_freq != 0 and
                grow(population[p].net, start_size, avg_degree)  #net, startsize, avgdegree
                #choice of GROWTH FUNCTION, eventually dyn slows
                #if (p == 0): console_report(population[0])

            # mutation
            for node in population[p].net.nodes():
                if (random.random() < mut_freq):
                    mutate(population[p].net, node, mut_bias)

            population[p].fitness_parts = pressurize(population[p].net, pressure, tolerance, knapsack_solver, fitness_type)
            if ((fitness_type == 0) or (fitness_type == 2) or (fitness_type == 3) or (fitness_type == 10) or (fitness_type == 12) or (fitness_type == 14)):
                max_feature1 = max(max_feature1, population[p].fitness_parts[0])
                max_feature2 = max(max_feature2, population[p].fitness_parts[1])
            elif ((fitness_type == 1 ) or (fitness_type == 4) or (fitness_type == 5) or (fitness_type == 6)):
                population[p].fitness = population[p].fitness_parts[0]
            elif ((fitness_type == 7)):
                population[p].fitness = population[p].fitness_parts[0] + population[p].fitness_parts[1]
            elif ((fitness_type == 8) or (fitness_type==9) or (fitness_type==11) or (fitness_type==13)):
                population[p].fitness = population[p].fitness_parts[0] * population[p].fitness_parts[1]
            else: print("unknown fitness type")

        if ((fitness_type == 0) or (fitness_type == 3)): pareto_rank(population)
        elif ((fitness_type == 1) or (fitness_type == 4) or (fitness_type == 5) or (fitness_type == 6) or (fitness_type == 7) or (fitness_type == 8) or (fitness_type == 9) or (fitness_type == 11) or (fitness_type == 13)):
            population.sort(key=operator.attrgetter('fitness'))
            population.reverse()
        elif (fitness_type == 2):
            generic_rank(population, 2)
            print("generic rank debug in evolve worker(): " + str(population[0].fitness) + " vs " + str(population[30].fitness))
        elif (fitness_type == 10 or (fitness_type == 12) or (fitness_type == 14)):
            for p in range(pop_size):
                population[p].fitness = population[p].fitness_parts[0]/max_feature1 * population[p].fitness_parts[1]/max_feature2
            population.sort(key=operator.attrgetter('fitness'))
            population.reverse()

        #breed, ocassionally cross, otherwise just replicates
        if (cross_freq != 0 and g % int(1 / cross_freq) == 0): cross_fraction = crossover_fraction
        else:                                                  cross_fraction = 0
        breed(population, num_survive, pop_size, cross_fraction)

    population.sort(key=operator.attrgetter('fitness'))
    population.reverse()  #if MAX'D, ex fitness_type 1
    #SHOULD BE UNNEC AS BREED ALREADY SUPPORTS, BUT CHECK
    #print("In worker " + str(worker_ID) + ": Most fit=" + str(population[0].fitness) + " vs least fit=" + str(population[len(population) - 1].fitness))

    #write top founder_size pops to file
    for p in range(founder_size):
        netfile = output_dir + "/net/" + str(p) + ".txt"
        with open(netfile, 'wb') as net_out:
            nx.write_edgelist(population[p].net, net_out)   #make sure overwrites
        #also write info like population[p].fitness somewhere?

    #output.outro_csv(output_dir, gens*output_freq, pop_size)

    print("Worker " + str(worker_ID) + " finished.")


def evolve_master(configs):
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




def evolve_master_old(population, subpop_gens, num_survive, crossover_percent, mutation_chance, output_dir,  pressure, tolerance, knapsack_solver):
    pop_size = len(population)

    output_dir += "/master/"
    #breed(population, num_survive, pop_size, crossover_percent, mutation_chance)

    for g in range(subpop_gens):
        max_RGGR = max_ETB = 0

        for p in range(pop_size):
            if (grow_freq != 0 and g % int(gens*grow_freq)):
                grow(population[p].net, 10, avg_degree)  #net, startsize, avgdegree
                #choice of GROWTH FUNCTION
                #g%int(math.log(grow_freq)) == 0): ?
                if (p == 0): console_report(population[0])

            population[p].fitness_parts = pressurize(population[p].net, pressure, tolerance, knapsack_solver)
            max_RGGR = max(max_RGGR, population[p].fitness_parts[0])
            max_ETB = max(max_ETB, population[p].fitness_parts[1])
            #print(population[p].fitness_parts)

        for p in range(pop_size):
            population[p].fitness = .5*population[p].fitness_parts[0]/max_RGGR + .5*population[p].fitness_parts[1]/max_ETB
            #might want to check that max_RGGR and max_ETB != 0 and throw warning if are (and divide by 1)

        breed(population, num_survive, pop_size, crossover_percent, mutation_chance)
        if (output_freq != 0 and g % int(gens/output_freq) == 0): output.to_csv(population, output_dir)  # need to write output.worker_csv()

    population.sort(key=operator.attrgetter('fitness'))
    #as in breed(), check that sorts with MAX fitness first

    return population


def gen_init_population(init_type, start_size, pop_size):
    if (init_type == 0):
        population = [Net(nx.DiGraph(), i) for i in range(pop_size)]
        for p in range(pop_size):
            grow(population[p].net, start_size, 1)

    else:
        print("ERROR in gen_init_population(): unknown init_type.")
        return

    return population


def grow(net, startSize, avg_degree):
    #operates only on nodes
    #adds edges to or from a new node

    # add numbered node
    node = len(net.nodes())
    net.add_node(node)

    if (len(net.nodes()) >= 2): #if size 1 would add an extra node

        for i in range(avg_degree):
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

    #keep growing if < startSize
    while (len(net.nodes()) < startSize): grow(net, startSize, avg_degree)


    #ASSUMPTION: net should remain connected
    connect_components(net)


def init_worker_dirs(num_workers, output_dir):
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

def mutate(net, node, bias):
    #operates on edges of given node
    #bias is boolean and prefs adding edges to nodes with high degree and vice versa

    # mutation options: rm edge, add edge, change edge sender or target, change edge sign, reverse edge direction

    mut_type = random.random()
    if (len(net.out_edges(node)) != 0):

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
                node2 = node
                while (node2 == node):
                    node2 = random.SystemRandom().sample(net.nodes(), 1)
                    node2 = node2[0]
                sign = random.randint(0, 1)
                if (sign == 0):     sign = -1
                net.add_edge(node, node2, sign=sign)

            else:
                # rm edge
                edge = random.SystemRandom().sample(net.out_edges(node), 1)
                edge = edge[0]
                net.remove_edge(edge[0], edge[1])

                # ASSUMPTION: net should remain connected
                while (not nx.is_weakly_connected(net)): connect_components(net)

        elif(mut_type < .6):
            #rewire: change an edge node

            edge = random.SystemRandom().sample(net.out_edges(node), 1)
            edge = edge[0]
            net.remove_edge(edge[0], edge[1])
            node2 = node
            while (node2 == node):  #find a new target node
                node2 = random.SystemRandom().sample(net.nodes(), 1)
                node2 = node2[0]
            sign = random.randint(0, 1)
            if (sign == 0):     sign = -1

            net.add_edge(node, node2, sign=sign)

            # ASSUMPTION: net should remain connected
            while (not nx.is_weakly_connected(net)): connect_components(net)

        elif (mut_type < .8):
            #change direction of edge
            edge = random.SystemRandom().sample(net.out_edges(node), 1)
            edge = edge[0]
            sign = net[edge[0]][edge[1]]['sign']
            net.remove_edge(edge[0], edge[1])
            net.add_edge(edge[1], edge[0], sign=sign)


        else:
            #change edge sign
            edge = random.SystemRandom().sample(net.out_edges(node), 1)
            edge = edge[0]
            net[edge[0]][edge[1]]['sign'] = -1*net[edge[0]][edge[1]]['sign']


    else:   #NO OUT EDGES, same prob of adding as if have out edges, otherwise do nothing
        if (random.random() < .2):
            if (bias == True):
                ngh_deg = nx.average_neighbor_degree(net, nodes=[node])
                ngh_deg = ngh_deg[node]
                if (ngh_deg != 0):
                    add_prob = (net.degree(node)) / (ngh_deg + net.degree(node))
                else:
                    add_prob = .5
            else:
                add_prob = .5

            if (random.random() < add_prob):
                # add edge
                node2 = node
                while (node2 == node):
                    node2 = random.SystemRandom().sample(net.nodes(), 1)
                    node2 = node2[0]
                sign = random.randint(0, 1)
                if (sign == 0):     sign = -1
                net.add_edge(node, node2, sign=sign)


def pressurize(net, pressure_relative, tolerance, knapsack_solver, fitness_type, num_samples_relative):
    #does all the reducing to kp and solving
    #how can it call configs without being passed???

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
            GENES_in, GENES_out, coresize, execution_time = a_result[4], a_result[5], a_result[9], a_result[10]
            total_benefit = a_result[0]
            total_dmg = a_result[1]
            num_green = len(a_result[6])
            num_red = len(a_result[7])
            num_grey = len(a_result[8])
            # -------------------------------------------------------------------------------------------------
            for g in GENES_in:  # notice that green_genes is a subset of GENES_in
                Gs.append(
                    str(g[0]) + '$' + str(net.in_degree(g[0])) + '$' + str(net.out_degree(g[0])))
                Bs.append(g[1])
                Ds.append(g[2])
                Xs.append(1)
            for g in GENES_out:  # notice that red_genes is a subset of GENES_out
                Gs.append(
                    str(g[0]) + '$' + str(net.in_degree(g[0])) + '$' + str(net.out_degree(g[0])))
                Bs.append(g[1])
                Ds.append(g[2])
                Xs.append(0)

            # Gs, Bs, Ds, Xs are, respectively,
            # the genes
            # their corresponding benefits
            # their corresponding weights (damages)
            # the solution vector (a binary 0/1 sequence, 0 = outside knapsack, 1=inside knapsack)

            #hub score eval
            soln_bens = []
            for g in range(len(Bs)):
                if (Xs[g] == 1):
                    inst_dist_in_sack += abs((Bs[g] - Ds[g]))
                    inst_dist_sq_in_sack += math.pow((Bs[g] - Ds[g]),2)
                    soln_bens.append(Bs[g])
            instance_ETB = sum(set(soln_bens))
            if (sum(soln_bens) != 0): inst_ETB_ratio = sum(set(soln_bens))/sum(soln_bens)
            else: inst_ETB_ratio = sum(set(soln_bens))

            #leaf score eval
            if (num_grey != 0):
                instance_RGGR = (num_green + num_red) / num_grey
            else:
                instance_RGGR = (num_green + num_red)
            inst_RGAllR = (num_green + num_red) / len(Bs)

        else:
            print ("WARNING in pressurize(): no results from oracle advice")

        ETB += instance_ETB
        RGGR += instance_RGGR
        dist_in_sack += inst_dist_in_sack
        dist_sq_in_sack += inst_dist_sq_in_sack
        ETB_ratio += inst_ETB_ratio
        RGAllR += inst_RGAllR

        #normalize by net size?

    ETB /= num_samples_relative
    RGGR /= num_samples_relative
    dist_in_sack /= num_samples_relative
    dist_sq_in_sack /= num_samples_relative
    ETB_ratio /= num_samples_relative
    RGAllR /= num_samples_relative

    if (fitness_type == 0 or fitness_type == 1):
        return [RGGR, ETB]
    elif (fitness_type == 2 or fitness_type == 3):
        return [RGAllR, ETB]
    elif (fitness_type == 4 or fitness_type == 5):
        return [RGGR, dist_in_sack]
    elif (fitness_type == 6 or fitness_type == 7):
        return [RGAllR, dist_in_sack]
    else: print("ERROR in pressurize(): unknown fitness type.")


def read_in_workers(num_workers, population, output_dir, num_return):
    for w in range(num_workers):
        for p in range(num_return):
            net_file = output_dir + str(w) + "/net/" + str(p) + ".txt"
            population[w*num_return+p].net = nx.read_edgelist(net_file, nodetype=int, create_using=nx.DiGraph())
            char_file = output_dir + str(w) + "/net_chars/" + str(p) + ".csv"
            with open(char_file, 'r') as net_char_file:
                chars = net_char_file.readline().split(",")
                population[w * num_return + p].fitness = float(chars[0])
                population[w * num_return + p].fitness_parts[0] = float(chars[1])
                population[w * num_return + p].fitness_parts[1] = float(chars[2])

    return population


def write_out_worker(num_return, population, output_dir):
    # write top nets to file
    for p in range(num_return):
        netfile = output_dir + "/net/" + str(p) + ".txt"
        with open(netfile, 'wb') as net_out:
            nx.write_edgelist(population[p].net, net_out)
        netfile = output_dir + "/net_chars/" + str(p) + ".csv"
        with open(netfile, 'w') as chars_out:
            #fitness, fitness_parts, id
            chars_out.write(str(population[p].fitness) + "," + str(population[p].fitness_parts[0]) + "," + str(population[p].fitness_parts[1]) + "," + str(population[p].id))


#RETIRED FUNCTIONS (may be of use for reference)

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

def generic_rank(population, num_features):
    #assumes that each feature intends to be MAXED

    for p in range(len(population)):
        population[p].fitness = 0

    for i in range(num_features):
        for p in range(len(population)):
            population[p].temp = population[p].fitness_parts[i]
        population.sort(key=operator.attrgetter('temp'))
        for p in range(len(population)):
            population[p].fitness += p

    population.sort(key=operator.attrgetter('fitness'))
    population.reverse()


def unused():
    #storage for unused functions

    for g in range(gens):
        #UNPARALLIZED


        '''PRE PARALLEL
        output.init_csv(pop_size, num_workers, output_dir, configs)
        evolve_master(population, merge_gens, num_survive, crossover_percent, mutation_chance, output_dir, pressure, tolerance, knapsack_solver)

        print ("\nEvolution starting...")
        for g in range(gens):

            for n in range(num_workers):
                population = [Net(M.copy(), i) for i in range(pop_size)]
                evolve_worker(n, population, num_workers, subpop_gens, num_survive,crossover_percent, mutation_chance,output_dir,  pressure, tolerance, configs)


            print("Master gen " + str(g) + " starting.")

            #read in nets from files
            for n in range(num_workers):
                in_dir = output_dir + str(n)
                for s in range(subpop_size):
                    netfile = in_dir + "/net/" + str(s) + ".txt"    #depends on output.worker_csv() format
                    population[n*subpop_size+s].net = nx.read_edgelist(netfile, create_using=nx.DiGraph())
                    #change population fitnesses, ect
                    #diff size nets due to unevolved nets, but should breed()

        #evolve_popn before giving back out to workers i think
        evolve_master(population, merge_gens, num_survive, crossover_percent, mutation_chance, output_dir,  pressure, tolerance, knapsack_solver)
        #(population, subpop_gens, num_survive, crossover_percent, mutation_chance, output_dir,  pressure, tolerance, knapsack_solver)
        '''

        ''' PARALLEL VERSION
        #handle not int cases, warning -> change params, or diff size pops
        pool = mp.Pool(num_workers)
        args = []
        barrier= mp.Barrier(num_workers-1) #why does -1 seem to work?

        for n in range(num_workers):
            #subpop = mp.Process(target=evolve_population_worker, args=(n, population[subpop_size*n:subpop_size*[n+1]], num_workers, subpop_gens, num_survive,crossover_percent, mutation_chance,output_dir,  pressure, tolerance, knapsack_solver))
                #check subpopn indices
                #shitload of params, maybe way to pass a bunch initially and only subset as time goes on
                #params: (worker_ID, founder_pop, num_workers, subpop_gens, num_survive, crossover_percent, mutation_chance,output_dir)
            args.append([n, population[subpop_size*n:subpop_size*(n+1)], num_workers, subpop_gens, num_survive,crossover_percent, mutation_chance,output_dir,  pressure, tolerance, configs])


        pool.starmap(evolve_worker, args)

        #WAIT for all jobs to finish (synch pt/bottleneck)
        #barrier.wait()
        pool.join()
        pool.close()
        '''



#FULL ALGORITHM RUN FNS()

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


def simple_evolve(configs):
    #a lot of configs are modified from orig to allow dynamic resizing with diff net sizes
    knapsack_solver     = cdll.LoadLibrary(configs['KP_solver_binary'])
    pressure            = math.ceil ((float(configs['PT_pairs_dict'][1][0])/100.0))  #why not just pressure? SHOULD CHANGE
    tolerance           = configs['PT_pairs_dict'][1][1]
    gens = int(configs['generations'])
    pop_size = int(configs['population_size'])
    population = [Net(M.copy(),i) for i in range(pop_size)]
    fitness = [0 for i in range(pop_size)]  #unused i think
    survive_fraction = float(configs['percent_survive'])/100
    num_survive = int(pop_size*survive_fraction)

    num_samples = configs['sampling_rounds']
    max_samples = configs['sampling_rounds_max']
    mutation_freq = float(configs['mutation_frequency'])
    crossover_fraction = float(configs['crossover_percent'])/100
    avg_degree = int(configs['average_degree'])
    output_file = configs['output_file']
    output_dir = configs['output_directory'].replace("v4nu_minknap_1X_both_reverse/", '')  #no idea where this is coming from
    grow_freq = float(configs['growth_frequency'])
    output_freq = float(configs['output_frequency'])
    start_size = int(configs['starting_size'])
    grow_freq = float(configs['growth_frequency'])

    num_workers = int(configs['number_of_workers'])
    #num_workers = mp.cpu_count() #override
    subpop_size = int(pop_size / num_workers)

    output.init_csv(pop_size, num_workers, output_dir, configs)
    #evolve_master(population, merge_gens, num_survive, crossover_percent, mutation_chance, output_dir, pressure, tolerance, knapsack_solver)

    if (crossover_fraction + survive_fraction > 1): print("WARNING: crossover + surviving percents > 100.")

    print ("\nEvolution starting...")
    for p in range(pop_size):
        grow(population[p].net, start_size, avg_degree)

    for n in range(num_workers):
        population_copy = [population[p].copy() for p in range(pop_size)]
        evolve_worker(n, population_copy, num_workers, gens, num_survive,crossover_fraction, mutation_freq,output_dir,  pressure, tolerance, grow_freq, configs)

    print("Done evolving workers, generating images.")
    plot_nets.features_over_time(output_dir,num_workers,gens,pop_size, output_freq)
    plot_nets.fitness_over_params(output_dir, num_workers)


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




