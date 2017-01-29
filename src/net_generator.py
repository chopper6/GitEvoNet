import networkx as nx
from random import SystemRandom as sysRand

# maybe rename to reduce confusion
class Net:
    def __init__(self, net, id):
        self.fitness = 0    #aim to max
        self.fitness_parts = [0]*3   #leaf-fitness, hub-fitness
        self.net = net.copy()
        assert(self.net != net)
        self.id = id  #irrelv i think

    def copy(self):
        copy = Net(self.net, self.id)
        copy.fitness = self.fitness
        self.fitness_parts = [0]*3   #leaf-fitness, hub-fitness
        assert (copy != self and copy.net != self.net)
        #assert (copy.fitness_parts != self.fitness_parts)
        return copy


def init_population(init_type, start_size, pop_size):

    if (init_type == 0):
        population = [Net(nx.DiGraph(), i) for i in range(pop_size)] #change to generate, based on start_size

    elif (init_type == 1):
        population = [Net(nx.erdos_renyi_graph(start_size,.01, directed=True, seed=None), i) for i in range(pop_size)]

    elif (init_type == 2):
        population = [Net(nx.empty_graph(start_size, create_using=nx.DiGraph()), i) for i in range(pop_size)]

    elif (init_type == 3):
        #crazy high run time due to about n^n edges
        population = [Net(nx.complete_graph(start_size, create_using=nx.DiGraph()), i) for i in range(pop_size)]

    elif (init_type == 4):
        population = [Net(nx.cycle_graph(start_size, create_using=nx.DiGraph()), i) for i in range(pop_size)]

    elif (init_type == 5):
        population = [Net(nx.star_graph(start_size), i) for i in range(pop_size)]
        custom_to_directed(population)

    elif (init_type == 6):  #highly connected eR
        population = [Net(nx.erdos_renyi_graph(start_size,.015, directed=True, seed=None), i) for i in range(pop_size)]


    elif (init_type == 7):  # curr does not work, since can't go to undirected for output
        population = [Net(nx.scale_free_graph(start_size),i) for i in range(pop_size)]
    elif (init_type == 8):
        population = [Net(nx.barabasi_albert_graph(start_size, 2),i) for i in range(pop_size)]
        custom_to_directed(population)
    elif (init_type == 9):
        population = [Net(nx.barabasi_albert_graph(start_size, 1),i) for i in range(pop_size)]
        custom_to_directed(population)

    else:
        print("ERROR in master.gen_init_population(): unknown init_type.")
        return


    sign_edges(population)

    return population


def custom_to_directed(population):
    # changes all edges to directed edges
    # rand orientation of edges
    #note that highly connected graphs should merge directing and signing edges to one loop

    for p in range(len(population)):
        edge_list = population[p].net.edges()
        del population[p].net

        population[p].net = nx.DiGraph(edge_list)
        edge_list = population[p].net.edges()
        for edge in edge_list:
            if (sysRand().random() < .5):  #50% chance of reverse edge
                population[p].net.remove_edge(edge[0], edge[1])
                population[p].net.add_edge(edge[1], edge[0])




def sign_edges(population):
    for p in range(len(population)):
        edge_list = population[p].net.edges()
        for edge in edge_list:
            sign = sysRand().randint(0, 1)
            if (sign == 0):     sign = -1
            population[p].net[edge[0]][edge[1]]['sign'] = sign
