
import networkx as nx


def reset_fitness(net):
    for n in net.nodes():
        net.node[n]['fitness'] = 0

def reset_BDs(net):
    for n in net.nodes():
        net.node[n]['benefits'] = 0
        net.node[n]['damages'] = 0

def normz_by_num_instances(net, num_instances):
    if (num_instances == 0):
        print("WARNING: node_fitness(): # instances = 0")
        return
    for n in net.nodes():
        pre = net.node[n]['fitness']
        net.node[n]['fitness'] /= float(num_instances)
        #print(pre, net.node[n]['fitness'])

