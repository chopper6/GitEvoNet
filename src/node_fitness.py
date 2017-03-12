import math, os, csv

def append_pair (nodeFitness, B, D, leaf_metric, hub_metric, fitness_operator):
    # TODO: handle fitness in more elegant manner
    # TODO: currently assumes only leaf_metric as fitness

    # node_fitness[B][D] = freq, fitness
    if (B >= len(nodeFitness) or D >= len(nodeFitness)): 
        print("Warning node_fitness(): oversized node not included, B = " + str(B) + ", D = " + str(D))
        return nodeFitness

    nodeFitness[B][D][0] += 1
    if (nodeFitness[B][D][1] == 0): #ASSUMES matrix is init to 0
        fitness = 0
        if (leaf_metric == 'RGAR' or leaf_metric == 'RGMG'):
            if (B == 0 or D == 0): fitness = 1
            else: fitness = 0
        elif (leaf_metric == 'ratio'):
            if (B+D > 0): fitness = max(B,D)/(B+D)
        elif (leaf_metric == 'ratio sq'):
            if (B+D>0): fitness = math.pow(max(B,D)/(B+D), 2)
        elif (leaf_metric == 'ratio btm sq'):
            if (B+D>0): fitness = max(B,D)/(math.pow(B+D, 2))
        elif (leaf_metric == 'dual 1'):
            if (B+D>0): fitness = math.pow(B - D, 2) / (B + D)
        else: print("ERROR in node_fitness: Unknown leaf_metric " + str(leaf_metric) + " , maybe add?")
        nodeFitness[B][D][1] = fitness

    return nodeFitness

def read_in(file, net):
    #TODO: curr assumes net does NOT change size and so initial matrix is sufficient size

    max_val = len(net.edges())
    node_fitness = [[[0, 0] for i in range(max_val)] for j in range(max_val)]

    if (os.path.exists(file)):
        all_lines = [Line.strip() for Line in (open(file,'r')).readlines()]
        for line in all_lines[1:]:
            line = line.split(",")
            if (len(line) != 4): print("ERROR in node_fitness: file should have 4 entries on each line: B,D,freq,fitness")
            line[-1].replace("\n",'')
            B = int(line[0])
            D = int(line[1])
            freq = int(line[2])
            fitness = float(line[3])

            node_fitness[B][D] = [freq,fitness]

    return node_fitness

def write_out(file, node_fitness):
    with open(file, 'w') as out_file:

        if (node_fitness==None): return #just used to wipe file

        output = csv.writer(out_file)
        for B in range(len(node_fitness)):
            for D in range(len(node_fitness[B])):
                output.writerow([B,D,node_fitness[B][D][0], node_fitness[B][D][1]])

def normz(nodeFitness, fraction):
    for B in range(len(nodeFitness)):
        for D in range(len(nodeFitness[B])):
            nodeFitness[B][D][0] /= fraction

    return nodeFitness
