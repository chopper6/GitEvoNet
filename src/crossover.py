#not integrated at the moment

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
