import os, math
import numpy as np
import leaf_fitness, BD_plots, slice_plots


def analyze(output_dir):
    dirr = output_dir + "instances/"

    node_info, iters, leaf_metric = read_in(dirr)
    # node_info = {'id':names, 'degree':deg, 'benefit':B, 'damage':D, 'solution':soln}
    # 'benefit' = [file#] [node#]

    freq, maxBD = extract_freq(node_info)
    # freq [file#] [B] [D]

    Pr = BD_probability(maxBD)
    # Pr [B] [D]

    BD_leaf_fitness = calc_BD_leaf_fitness(leaf_metric, maxBD) #derive leaf metric from file name?
    # BD_leaf_fitness [B] [D]

    ETB_score = derive_ETB(node_info, maxBD)
    # ETB_score [file#] [B] [D]


    ####PLOTS####
    if not os.path.exists(output_dir + "/BD_plots/"):
        os.makedirs(output_dir + "/BD_plots/")
    if not os.path.exists(output_dir + "/slice_plots/"):
        os.makedirs(output_dir + "/slice_plots/")


    plot_dir = output_dir + "BD_plots/"
    BD_plots.freq(plot_dir, freq, iters)
    BD_plots.probability(plot_dir, Pr)
    BD_plots.leaf_fitness(plot_dir, BD_leaf_fitness)
    BD_plots.Pr_leaf_fitness(plot_dir, Pr, BD_leaf_fitness)
    BD_plots.ETB(plot_dir, ETB_score, iters)

    plot_dir = output_dir + "slice_plots/"
    slice_plots.leaf_fitness(plot_dir, Pr, BD_leaf_fitness)
    slice_plots.ETB(plot_dir, ETB_score, iters)



def derive_ETB(node_info, maxBD):

    num_files = len(node_info['benefits'])
    num_nodes = len(node_info['benefits'][-1])
    ETB_score = np.zeros((num_files, maxBD, maxBD))

    for i in range(num_files):
        solnB, solnD = [], []
        for j in range(num_nodes):
            if (node_info['solution'][i][j] == 1):
                solnB.append(node_info['benefits'][i][j])
                solnD.append(node_info['damages'][i][j])

        soln_freq = np.bincount(np.array(solnB))
        denom = sum(solnB)

        for j in range(len(solnB)):
            B = solnB[j]
            D = solnD[j]
            node_contrib = (B / soln_freq[B])/denom
            ETB_score[i][B][D] += node_contrib

    return ETB_score



def calc_BD_leaf_fitness(leaf_metric, maxBD):
    BD_leaf_fitness = np.zeros((maxBD,maxBD))

    for B in range(maxBD):
        for D in range(maxBD):
            BD_leaf_fitness[B][D] = leaf_fitness.node_score(leaf_metric, B, D)

    return BD_leaf_fitness

def BD_probability(maxBD):
    Pr = np.empty((maxBD, maxBD))

    for B in range(maxBD):
        for D in range(maxBD):
            if (B+D==0):
                Pr[B][D] = 0
            else:
                pr = math.pow(.5, B+D)
                div = B+D
                combos = math.factorial(B+D)/math.factorial(B)*math.factorial(D)
                Pr[B][D] = pr*combos/div

    return Pr


def extract_freq(node_info):
    maxBD = (max(np.max(node_info['benefits']), np.max(node_info['damages'])))
    maxBD = int(maxBD)+1
    num_files = len(node_info['benefits'])

    print("Instances.extract_freq(): maxBD = " + str(maxBD) + ", num files = " + str(num_files))
    print("Instances.extract_freq(): len node_info['ben'][0] = " + str(len(node_info['benefits'][0])))

    freq = np.zeros((num_files, maxBD, maxBD))

    for i in range(num_files):
        num_nodes = len(node_info['benefits'][i])

        for j in range(num_nodes):
            B = node_info['benefits'][i][j]
            D = node_info['damages'][i][j]
            freq[i][B][D] += 1

        if (num_nodes != 0): np.divide(freq[i], num_nodes)

    print("Instances.extract_freq(): Max BD freq = " + str(np.max(freq)))
    return freq, maxBD


def read_in(dirr):

    files = os.listdir(dirr)
    num_iters = len(files)

    with open(dirr + files[-1], 'r') as sample:
        #assumes last file has largest number of nodes
        all_lines = [line.strip() for line in sample.readlines()]
        line = all_lines[0].split(' ')
        num_nodes = len(line)
        title = files[-1].split("_")
        leaf_metric = title[0].split("multiply")
        leaf_metric = leaf_metric[0]

    for file in os.listdir(dirr):
        all_lines = [line.strip() for line in (open(dirr + file, 'r')).readlines()]
        for line in all_lines:
            line = line.split(' ')
            num_nodes = max(len(line), num_nodes)

    print("Instances.read_in(): num nodes = " + str(num_nodes) + ", leaf metric = " + str(leaf_metric))



    names = np.zeros((num_iters, num_nodes), dtype=np.int)
    deg = np.zeros((num_iters, num_nodes), dtype=np.int)
    B = np.zeros((num_iters, num_nodes), dtype=np.int)
    D = np.zeros((num_iters, num_nodes), dtype=np.int)
    soln = np.zeros((num_iters, num_nodes), dtype=np.int)


    file_num=0
    iters = []
    for file in os.listdir(dirr):
        all_lines = [line.strip() for line in (open(dirr + file, 'r')).readlines()]
        iter = file.split("X")
        iters.append(int(iter[2].replace(".csv", '').replace('iter','')))

        line_num = 0
        for line in all_lines:
            line = line.split(' ')

            #name & degree
            if (line_num % 5 == 0):
                node_num=0
                for node in line:
                    node = node.split('$')
                    name = node[0]
                    degree = int(node[1]) + int(node[2])

                    names[file_num][node_num] = name
                    deg [file_num][node_num] = degree

                    node_num += 1

            #benefits
            elif (line_num % 5 == 1):
                node_num = 0
                for node in line:
                    B[file_num][node_num] = int(node)
                    node_num += 1

            #damages
            elif (line_num % 5 == 2):
                node_num = 0
                for node in line:
                    D[file_num][node_num] = int(node)
                    node_num += 1

            #solution
            elif (line_num % 5 == 3):
                node_num = 0
                for node in line:
                    soln[file_num][node_num] = int(node)
                    node_num += 1

            #don't track last line, curr holds exe time

            line_num+=1
        file_num+=1

    node_info = {'id':names, 'degree':deg, 'benefits':B, 'damages':D, 'solution':soln}
    return node_info, iters, leaf_metric
