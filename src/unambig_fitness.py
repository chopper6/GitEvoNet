from scipy.special import comb as nchoosek
import math, numpy as np, networkx as nx, pickle, os
log10 = math.log10
def l1(s):
    return str(s).ljust(10,' ')
def l(s):
    return str(s).ljust(7,' ')
################################### Fitness function #########################################
def unambiguity_fitness_score(G): # G is a networkx DiGraph (one of your population of networks)
    n2e     = 0.5
    e2n     = 2.0
    p       = .5 
    q       = 1 - p
    fitness = []
    for d in G.degree().values():
        if d == 0:
            fitness.append(0)
            continue
        if d>300:
            d = 300
        unambiguity = []
        for k in range(0,d+1,1):
            dCk          = nchoosek(d,k,exact=True) 
            count        = dCk   *   p**k   *   q**(d-k)
            unambiguity.append(n2e*(count**(e2n*log10(d)))) # winner
        fitness.append(np.average(unambiguity))
    return np.average(fitness)
###############################################################################################


for root, dirs, files in os.walk('networks/'):
    for f in [f for f in files if f.split('.')[1]=='dump']:
        network = None
        with open (os.path.join(root,f),'rb') as dump:
            network = pickle.load(dump)
        print(l1(f.split('.')[0])+" : "+l(len(network.nodes()))+'  nodes,  '+l(len(network.edges()))+'  edges, fitness = '+l(unambiguity_fitness_score(network)))

network = nx.complete_graph(100)
print(l1("Complete")+" : "+l(len(network.nodes()))+'  nodes,  '+l(len(network.edges()))+'  edges, fitness = '+l(unambiguity_fitness_score(network)))
network =  nx.configuration_model ([1 for e in range(3352)])
print(l1("All leafs")+" : "+l(len(network.nodes()))+'  nodes,  '+l(len(network.edges()))+'  edges, fitness = '+l(unambiguity_fitness_score(network)))
network =  nx.configuration_model ([2 for e in range(3352)])
print(l1("All 2s")+" : "+l(len(network.nodes()))+'  nodes,  '+l(len(network.edges()))+'  edges, fitness = '+l(unambiguity_fitness_score(network)))
network =  nx.configuration_model ([3 for e in range(3352)])
print(l1("All 3s")+" : "+l(len(network.nodes()))+'  nodes,  '+l(len(network.edges()))+'  edges, fitness = '+l(unambiguity_fitness_score(network)))

