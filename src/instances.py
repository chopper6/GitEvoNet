import os, math, sys
import numpy as np
import leaf_fitness
import BD_plots, slice_plots
from time import process_time as ptime

def analyze(output_dir):
    dirr = output_dir + "instances/"

    t0 = ptime()
    node_info, iters, leaf_metric = read_in(dirr)
    # node_info = {'id':names, 'degree':deg, 'benefit':B, 'damage':D, 'solution':soln}
    # 'benefit' = [file#] [node#]
    t1 = ptime()
    print("\nRead_in took " + str(t1-t0))

    #TEMP FOR HUBS:
    #leaf_metric = "RGAR"

    t0 = ptime()
    freq, maxBD = extract_freq(node_info)
    t1 = ptime()
    print("\nExtract_freq took " + str(t1-t0))

    t0 = ptime()
    Pr = BD_probability(maxBD)
    t1 = ptime()
    print("\nProbability took " + str(t1-t0))
    # Pr [B] [D]

    t0 = ptime()
    BD_leaf_fitness = calc_BD_leaf_fitness(leaf_metric, maxBD) #derive leaf metric from file name?
    # BD_leaf_fitness [B] [D]
    t1 = ptime()
    print("\nCalc_leaf_fitness took " + str(t1-t0))

    t0 = ptime()
    #ETB_score = derive_ETB(node_info, maxBD)
    # ETB_score [file#] [B] [D]
    t1 = ptime()
    print("\nDerive_ETB took " + str(t1-t0))

    ####PLOTS####
    if not os.path.exists(output_dir + "/BD_plots/"):
        os.makedirs(output_dir + "/BD_plots/")
    if not os.path.exists(output_dir + "/slice_plots/"):
        os.makedirs(output_dir + "/slice_plots/")

    t0 = ptime()
    plot_dir = output_dir + "BD_plots/"
    BD_plots.freq(plot_dir, freq, iters)
    BD_plots.probability(plot_dir, Pr)
    BD_plots.leaf_fitness(plot_dir, BD_leaf_fitness)
    BD_plots.Pr_leaf_fitness(plot_dir, Pr, BD_leaf_fitness)
    #BD_plots.ETB(plot_dir, ETB_score, iters)

    plot_dir = output_dir + "slice_plots/"
    slice_plots.leaf_fitness(plot_dir, Pr, BD_leaf_fitness, None)
    #slice_plots.ETB(plot_dir, ETB_score, iters)

    t1 = ptime()
    print("\nPlots took " + str(t1-t0))


def derive_ETB(node_info, maxBD):

    num_files = len(node_info['benefits'])
    num_instances = len(node_info['benefits'][-1])
    num_nodes = len(node_info['benefits'][-1][0])
    ETB_score = np.zeros((num_files, maxBD, maxBD))

    ct, ft, dt, ft = 0,0,0,0

    for i in range(num_files):
        solnB, solnD = [], []
        for j in range(num_instances):
            t0 = ptime()
            for k in range(num_nodes):
                if (node_info['solution'][i][j][k] == 1):
                    solnB.append(node_info['benefits'][i][j][k])
                    solnD.append(node_info['damages'][i][j][k])
            t1=ptime()
            ct += t1-t0

            t0 = ptime()
            soln_freq = np.bincount(np.array(solnB))
            denom = sum(solnB)
            t1 = ptime()
            ft += t1-t0

            t0 = ptime()
            for k in range(len(solnB)):
                B = solnB[k]
                D = solnD[k]
                node_contrib = (B / soln_freq[B])/denom
                ETB_score[i][B][D] += node_contrib
            t1 = ptime()
            dt += t1-t0
        
        t0=ptime()
        for j in range(maxBD):
            for k in range(maxBD):
                if (ETB_score[i][j][k] != 0): ETB_score[i][j][k] /= num_instances 
        t1=ptime()
        ft += t1-t0

  
    print("\nTime to collect solution = " + str(ct) + "\nTime to get greq in solution = " + str(ft) + "\nTime to get hub contrib = " + str(ct) + "\nTime to fill ETB_score = " + str(ft))
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
                combos = math.factorial(B+D)/(math.factorial(B)*math.factorial(D))
                Pr[B][D] = pr*combos
    return Pr


def extract_freq(node_info):
    maxBD = (max(np.max(node_info['benefits']), np.max(node_info['damages'])))
    maxBD = int(maxBD)+1
    num_files = len(node_info['benefits'])

    print("Instances.extract_freq(): maxBD = " + str(maxBD) + ", num files = " + str(num_files))
    print("Instances.extract_freq(): len node_info['ben'][0] = " + str(len(node_info['benefits'][0])))

    freq = np.zeros((num_files, maxBD, maxBD))

    for i in range(num_files):
        num_instances = len(node_info['benefits'][i])
        num_nodes = len(node_info['benefits'][i][0])

        for j in range(num_instances):
            for k in range(num_nodes):
                B = node_info['benefits'][i][j][k]
                D = node_info['damages'][i][j][k]
                freq[i][B][D] += 1

        if (num_instances != 0 and num_nodes !=0):
            for B in range(maxBD):
                for D in range(maxBD):
                    freq[i][B][D] /= num_instances*num_nodes

    print("Instances.extract_freq(): Max BD freq = " + str(np.max(freq)))
    return freq, maxBD


def read_in(dirr):

    files = os.listdir(dirr)
    num_iters = len(files)

    with open(dirr + files[0], 'r') as sample:
        #assumes last file has largest number of nodes
        all_lines = [line.strip() for line in sample.readlines()]
        num_instances = len(all_lines)/5
        if (num_instances % 1 != 0): print("ERROR: Instances.read_in(): num lines not evenly div by 5.\n")
        num_instances = int(num_instances)

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

    print("Instances.read_in(): num nodes = " + str(num_nodes) + ", leaf metric = " + str(leaf_metric) + ", num instances = " + str(num_instances))



    names = np.zeros((num_iters, num_instances, num_nodes), dtype=np.int)
    deg = np.zeros((num_iters, num_instances, num_nodes), dtype=np.int)
    B = np.zeros((num_iters, num_instances, num_nodes), dtype=np.int)
    D = np.zeros((num_iters, num_instances, num_nodes), dtype=np.int)
    soln = np.zeros((num_iters, num_instances, num_nodes), dtype=np.int)


    file_num=0
    iters = []
    for file in os.listdir(dirr):
        all_lines = [line.strip() for line in (open(dirr + file, 'r')).readlines()]
        iter = file.split("X")
        iters.append(int(iter[2].replace(".csv", '').replace('iter','')))

        line_num = 0
        for line in all_lines:
            line = line.split(' ')
            instance_num = math.floor(line_num/5)

            #name & degree
            if (line_num % 5 == 0):
                node_num=0
                for node in line:
                    node = node.split('$')
                    name = node[0]
                    degree = int(node[1]) + int(node[2])

                    #names[file_num][instance_num][node_num] = 0 #name
                    deg [file_num][instance_num][node_num] = degree

                    node_num += 1

            #benefits
            elif (line_num % 5 == 1):
                node_num = 0
                for node in line:
                    B[file_num][instance_num][node_num] = int(node)
                    node_num += 1

            #damages
            elif (line_num % 5 == 2):
                node_num = 0
                for node in line:
                    D[file_num][instance_num][node_num] = int(node)
                    node_num += 1

            #solution
            elif (line_num % 5 == 3):
                node_num = 0
                for node in line:
                    soln[file_num][instance_num][node_num] = int(node)
                    node_num += 1

            #don't track last line, curr holds exe time

            line_num+=1
        file_num+=1

    node_info = {'id':names, 'degree':deg, 'benefits':B, 'damages':D, 'solution':soln}
    return node_info, iters, leaf_metric


if __name__ == "__main__":
    #first bash arg should be parent directory, then each child directory
    dirr_base = "/home/2014/choppe1/Documents/EvoNet/virt_workspace/data/output/"

    if (sys.argv[1] == 'degreeFitness'):
        if not os.path.exists(dirr_base + "/degree_fitness/"):
            os.makedirs(dirr_base + "/degree_fitness/")
        for arg in sys.argv[2:]:
            leaf_metric = arg
            Pr = BD_probability(maxBD=20)
            BD_leaf_fitness = calc_BD_leaf_fitness(leaf_metric, maxBD=20)
            slice_plots.leaf_fitness(dirr_base+"/degree_fitness/", Pr, BD_leaf_fitness, leaf_metric)



    else:
        dirr_parent = sys.argv[1]
        dirr_base += dirr_parent

        for arg in sys.argv[2:]:
            print("Plotting dirr " + str(arg))
            dirr_addon = arg
            dirr= dirr_base + dirr_addon + "/"
            analyze(dirr)

        print("Finished analyzing instances.")

