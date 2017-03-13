import os, csv, math
import numpy as np

def add_instance(node_info, node_info_instance):
    node_features = {'freq', 'freq in solution', 'leaf', 'hub', 'fitness'}
    for feature in node_features:
        for B in range(len(node_info[feature])):
            for D in range(len(node_info[feature])):
                node_info[feature][B][D] += node_info_instance [feature][B][D]

def gen_node_info(max_val):
    # init node_info
    node_features = {'freq', 'freq in solution', 'leaf', 'hub', 'fitness'}
    node_info = [[[0 for i in range(max_val)] for j in range(max_val)] for k in node_features]
    return node_info

def normz(node_info, fraction, feature):
    for B in range(len(node_info)):
        for D in range(len(node_info[B])):
            node_info[B][D][feature] /= fraction

    return node_info


def read_in(dirr):

    files = os.listdir(dirr)
    num_in = len(files)
    num_features, max_B, header = 0, 0, None

    with open(files[0], 'r') as sample:
        all_lines = [line.strip() for line in sample.readlines()]
        header = all_lines[0][2:]
        num_features = len(header)
        max_B = math.pow(len(all_lines[1:]),.5)
        assert(max_B%1==0) #ie is int
        max_B = int(max_B)

    node_info = np.empty((num_in, max_B, max_B, num_features))
    print("\nin node_fitness.read_in(): node_info shape = " + str(np.shape(node_info)))

    file_num=0
    iters = []
    for file in os.listdir(dirr):
        all_lines = [line.strip() for line in (open(file, 'r')).readlines()]
        iters.append(int((file).replace(".csv",'')))
        for line in all_lines:
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
                    assert(node_info['freq'][B][D] * node_info['leaf'][B][D] + node_info['hub'][B][D] * node_info['freq in solution'][B][D] == node_info['fitness'][B][D])
                    output.writerow(row)
