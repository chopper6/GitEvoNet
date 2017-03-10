import matplotlib, os, math
matplotlib.use('Agg') # This must be done before importing matplotlib.pyplot
import matplotlib.pyplot as plt
import node_fitness

#TODO: make this more efficient, poss rm some plots
def BD_freq_fitness(output_dir, nodeFitness, net, file_name):
    # might want to normalize by # pressurize rounds

    check_dirs(output_dir)

    size = len(node_fitness)

    fitness, freqFit, freq = [[0 for i in range(size)] for j in range(size)],[[0 for i in range(size)] for j in range(size)],[[0 for i in range(size)] for j in range(size)]
    log_fitness, log_freqFit, log_freq = [[0 for i in range(size)] for j in range(size)], [[0 for i in range(size)] for j in range(size)],[[0 for i in range(size)] for j in range(size)]
    for B in range(size):
        for D in range(size):
            fitness[B][D] = node_fitness[B][D][1]
            freq[B][D] = node_fitness[B][D][0]
            freqFit[B][D] = node_fitness[B][D][0]*node_fitness[B][D][1]

            log_fitness[B][D] = math.log(node_fitness[B][D][1], 10)
            log_freq[B][D] = math.log(node_fitness[B][D][0], 10)
            log_freqFit[B][D] = math.log(node_fitness[B][D][0] * node_fitness[B][D][1], 10)

    #fitness plot
    plt.matshow(fitness, cmap=plt.get_cmap('plasma'))
    plt.ylabel("Benefits")
    plt.xlabel("Damages")
    plt.title("Fitness Each BD Pair")
    plt.colorbar()
    plt.savefig(output_dir + "/node_plots/fitness/" + str(file_name) + ".png")
    plt.clf()

    #freq plot
    plt.matshow(freq, cmap=plt.get_cmap('plasma'))
    plt.ylabel("Benefits")
    plt.xlabel("Damages")
    plt.title("Frequency Each BD Pair")
    plt.colorbar()
    plt.savefig(output_dir + "/node_plots/freq/" + str(file_name) + ".png")
    plt.clf()

    #fitness*freq plot
    plt.matshow(freqFit, cmap=plt.get_cmap('plasma'))
    plt.ylabel("Benefits")
    plt.xlabel("Damages")
    plt.title("Fitness*Frequency of Each BD Pair")
    plt.colorbar()
    plt.savefig(output_dir + "/node_plots/freqFitness/" + str(file_name) + ".png")
    plt.clf()

    #log fitness plot
    plt.matshow(log_fitness, cmap=plt.get_cmap('plasma'))
    plt.ylabel("Benefits")
    plt.xlabel("Damages")
    plt.title("Log-Scaled Fitness Each BD Pair")
    plt.colorbar()
    plt.savefig(output_dir + "/node_plots/log_fitness/" + str(file_name) + ".png")
    plt.clf()

    #log freq plot
    plt.matshow(log_freq, cmap=plt.get_cmap('plasma'))
    plt.ylabel("Benefits")
    plt.xlabel("Damages")
    plt.title("Log-Scaled Frequency Each BD Pair")
    plt.colorbar()
    plt.savefig(output_dir + "/node_plots/log_freq/" + str(file_name) + ".png")
    plt.clf()

    #log fitness_freq plot
    plt.matshow(log_freqFit, cmap=plt.get_cmap('plasma'))
    plt.ylabel("Benefits")
    plt.xlabel("Damages")
    plt.title("Log-Scaled Fitness*Frequency Each BD Pair")
    plt.colorbar()
    plt.savefig(output_dir + "/node_plots/log_freqFitness/" + str(file_name) + ".png")
    plt.clf()


def check_dirs(dirr):
    if not os.path.exists(dirr + "/node_plots/"):
        os.makedirs(dirr + "/node_plots/")

    if not os.path.exists(dirr + "/node_plots/freq"):
        os.makedirs(dirr + "/node_plots/freq")
    if not os.path.exists(dirr + "/node_plots/fitness"):
        os.makedirs(dirr + "/node_plots/fitness")
    if not os.path.exists(dirr + "/node_plots/freqFitness"):
        os.makedirs(dirr + "/node_plots/freqFitness")

    if not os.path.exists(dirr + "/node_plots/log_freq"):
        os.makedirs(dirr + "/node_plots/log_freq")
    if not os.path.exists(dirr + "/node_plots/log_fitness"):
        os.makedirs(dirr + "/node_plots/log_fitness")
    if not os.path.exists(dirr + "/node_plots/log_freqFitness"):
        os.makedirs(dirr + "/node_plots/log_freqFitness")

