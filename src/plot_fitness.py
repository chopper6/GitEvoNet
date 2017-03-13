import matplotlib, os, math
matplotlib.use('Agg') # This must be done before importing matplotlib.pyplot
import matplotlib.pyplot as plt
import node_fitness
import numpy as np

def BD_freq_fitness(output_dir):
    # might want to normalize by # pressurize rounds

    check_dirs(output_dir)
    node_info, iters, header = node_fitness.read_in(output_dir)

    num_files = len(node_info)
    max_B = len(node_info[0])
    num_features = len(header)

    # single feature plots
    for feature in range(num_features):
        dirr = output_dir + "/node_plots/" + str(header[feature]) + "/"
        zmax = max(node_info[:][:][:][feature])
        zmin = min(node_info[:][:][:][feature])
        for file in range(num_files):
            xydata = node_info[file][:][:][feature]

            plt.matshow(xydata, cmap=plt.get_cmap('plasma'), origin="lower", norm=matplotlib.colors.LogNorm(vmin=zmin, vmax=zmax), vmin=zmin, vmax=zmax)
            plt.ylabel("Benefits")
            plt.xlabel("Damages")
            plt.title(str(header[feature]) + " of Each BD Pair")
            plt.colorbar()
            plt.savefig(dirr + str(iters[file]) + ".png")
            plt.clf()
            plt.cla()

    # FOLLOWING PLOTS ARE DEPENDENT ON PARTICULAR FEATURES & THEIR POSITIONS
    # ['freq', 'freq in solution', 'leaf', 'hub', 'fitness']

    # leaf*freq
    dirr = output_dir + "/node_plots/LeafContrib/"
    zmax = max(node_info[:][:][:][0]*node_info[:][:][:][2])
    zmin = min(node_info[:][:][:][0]*node_info[:][:][:][2])

    for file in range(num_files):
        xydata = node_info[file][:][:][0]*node_info[file][:][:][2]

        plt.matshow(xydata, cmap=plt.get_cmap('plasma'), origin="lower", norm=matplotlib.colors.LogNorm(vmin=zmin, vmax=zmax), vmin=zmin, vmax=zmax)
        plt.ylabel("Benefits")
        plt.xlabel("Damages")
        plt.title("Contribution to Leaf Fitness of Each BD Pair")
        plt.colorbar()
        plt.savefig(dirr + str(iters[file]) + ".png")
        plt.clf()
        plt.cla()


    # hub*freq_in_soln
    dirr = output_dir + "/node_plots/HubContrib/"
    zmax = max(node_info[:][:][:][1] * node_info[:][:][:][3])
    zmin = min(node_info[:][:][:][1] * node_info[:][:][:][3])

    for file in range(num_files):
        xydata = node_info[file][:][:][1] * node_info[file][:][:][3]

        plt.matshow(xydata, cmap=plt.get_cmap('plasma'), origin="lower",norm=matplotlib.colors.LogNorm(vmin=zmin, vmax=zmax), vmin=zmin, vmax=zmax)
        plt.ylabel("Benefits")
        plt.xlabel("Damages")
        plt.title("Contribution to Hub Fitness of Each BD Pair")
        plt.colorbar()
        plt.savefig(dirr + str(iters[file]) + ".png")
        plt.clf()
        plt.cla()


    # leaf*freq + hub*freq_in_soln
    dirr = output_dir + "/node_plots/Fitness_Frequency/"
    zmax = max(node_info[:][:][:][0] * node_info[:][:][:][2] + node_info[:][:][:][1] * node_info[:][:][:][3])
    zmin = min(node_info[:][:][:][0] * node_info[:][:][:][2] + node_info[:][:][:][1] * node_info[:][:][:][3])

    for file in range(num_files):
        xydata = (node_info[:][:][:][0] * node_info[:][:][:][2] + node_info[:][:][:][1] * node_info[:][:][:][3])

        plt.matshow(xydata, cmap=plt.get_cmap('plasma'), origin="lower",norm=matplotlib.colors.LogNorm(vmin=zmin, vmax=zmax), vmin=zmin, vmax=zmax)
        plt.ylabel("Benefits")
        plt.xlabel("Damages")
        plt.title("Contribution to Fitness of Each BD Pair")
        plt.colorbar()
        plt.savefig(dirr + str(iters[file]) + ".png")
        plt.clf()
        plt.cla()







def check_dirs(dirr):
    if not os.path.exists(dirr + "/node_info/"):
        print("ERROR in plot_fitness: no directory to read in from, missing /node_info/.")
        return 1

    if not os.path.exists(dirr + "/node_plots/"):
        os.makedirs(dirr + "/node_plots/")

    if not os.path.exists(dirr + "/node_plots/freq"):
        os.makedirs(dirr + "/node_plots/freq")
    if not os.path.exists(dirr + "/node_plots/fitness"):
        os.makedirs(dirr + "/node_plots/fitness")
    if not os.path.exists(dirr + "/node_plots/freqFitness"):
        os.makedirs(dirr + "/node_plots/freqFitness")

