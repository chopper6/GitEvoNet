import os, csv, math
import numpy as np
import leaf_fitness, hub_fitness, fitness











#OLD CRAP
def calc(node_info, leaf_metric, hub_metric, fitness_operator, soln_bens, num_genes):
    max_size = len(node_info['freq']) #assumes all features have same size
    for B in range(max_size):
        for D in range(max_size):
            node_leaf = leaf_fitness.node_score(leaf_metric, B, D)
            node_leaf /= leaf_fitness.assign_denom(leaf_metric, num_genes)

            node_hub = hub_fitness.node_score(hub_metric, B, D, soln_bens)
            node_hub /= hub_fitness.assign_denom (hub_metric, soln_bens)

            node_info['leaf'][B][D] = node_leaf
            node_info['hub'][B][D] = node_hub #assumes in solution
            node_info['fitness'][B][D] = fitness.operate_on_features(node_leaf, node_hub, fitness_operator)

    return node_info



def add_instance(node_info, node_info_instance):
    node_features = ['freq', 'freq in solution', 'leaf', 'hub', 'fitness']
    for feature in node_features:
        for B in range(len(node_info[feature])):
            for D in range(len(node_info[feature])):
                node_info[feature][B][D] += node_info_instance [feature][B][D]
    return node_info


def gen_node_info(max_val):
    # init node_info
    node_features = ['freq', 'freq in solution', 'leaf', 'hub', 'fitness']
    node_feature_info =  [[[0 for k in range(max_val+1)] for i in range(max_val+1)] for j in range(len(node_features))]
    node_info = {node_features[i] : node_feature_info[i] for i in range(len(node_features))}
    return node_info


def normz(node_info, fraction, feature):
    if (feature == 'all'):
        node_features = {'freq', 'freq in solution', 'leaf', 'hub', 'fitness'}
        for feature in node_features:
            for B in range(len(node_info[feature])):
                for D in range(len(node_info[feature][B])):
                    node_info[feature][B][D] /= fraction

    else:
        for B in range(len(node_info[feature])):
            for D in range(len(node_info[feature][B])):
                if (fraction != 0): node_info[feature][B][D] /= fraction

    return node_info




def read_in(dirr):

    files = os.listdir(dirr)
    num_in = len(files)
    num_features, max_B, header = 0, 0, None

    with open(dirr + files[0], 'r') as sample:
        all_lines = [line.strip() for line in sample.readlines()]
        first_line = all_lines[0].split(",")
        header = first_line[2:]
        num_features = len(header)
        max_B = math.pow(len(all_lines[1:])/num_features,.5)
        assert(max_B%1==0) #ie is int
        max_B = int(max_B)

    node_info = np.empty((num_in, max_B, max_B, num_features))
    #print("\nin node_fitness.read_in(): node_info shape = " + str(np.shape(node_info)))

    file_num=0
    iters = []
    for file in os.listdir(dirr):
        all_lines = [line.strip() for line in (open(dirr + file, 'r')).readlines()]
        iters.append(int((file).replace(".csv",'')))
        for line in all_lines[1:]:
            line = line.split(",")
            B = int(line[0])
            D = int(line[1])
            for i in range(2,len(line)):
                node_info[file_num][B][D][i-2] = float(line[i])
        file_num+=1

    return node_info, iters, header


def write_out(file, node_info):

    with open(file, 'w') as out_file:

        if (node_info==None): return # just used to wipe file

        max_B = len(node_info['freq'])  # assumes all features have same max B,D
        output = csv.writer(out_file)

        node_features = ['freq', 'freq in solution', 'leaf', 'hub', 'fitness']
        output.writerow(['B', 'D','Frequency', 'Frequency in Solution', 'Leaf', 'Hub', 'Fitness'])
        for i in range(len(node_features)):
            for B in range(max_B):
                for D in range(max_B):
                    row = [B, D]
                    for i in range(len(node_features)):
                        row.append(node_info[node_features[i]][B][D])

                    #NOT SURE IF THE FOLLOWING NEC HOLDS
                    fit = node_info['fitness'][B][D] 
                    if (False): #fit != 0):
                        leaf_contrib = node_info['freq'][B][D] * node_info['leaf'][B][D]
                        hub_contrib = node_info['hub'][B][D] * node_info['freq in solution'][B][D] 
                        print("leaf: " + str(leaf_contrib) + "\t\t+ hub: " + str(hub_contrib) + "\t\t --> " + str(fit))
                    output.writerow(row)
