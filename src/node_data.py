
import networkx as nx


def reset_fitness(net):
    for node in net.nodes():
        net[node]['fitness'] = 0

def reset_BDs(net):
    for node in net.nodes():
        net[node]['benefits'] = 0
        net[node]['damages'] = 0

def normz_by_num_instances(net, num_instances):
    if (num_instances == 0):
        print("WARNING: node_fitness(): # instances = 0")
        return
    for node in net.nodes():
        net[node]['fitness'] /= float(num_instances)

