import matplotlib, os, math
matplotlib.use('Agg') # This must be done before importing matplotlib.pyplot
import matplotlib.pyplot as plt
import node_fitness
import numpy as np

def BD_freq_fitness(output_dir):
    # might want to normalize by # pressurize rounds
    if not os.path.exists(output_dir + "/node_info/"):
        print("ERROR in plot_fitness: no directory to read in from, missing /node_info/.")
        return 1
    node_info, iters, header = node_fitness.read_in(output_dir + "/node_info/")
    check_dirs(output_dir, header)

    num_files = len(node_info)
    max_B = len(node_info[0])
    num_features = len(header)
    # single feature plots
    for feature in range(num_features):
        dirr = output_dir + "node_plots/" + str(header[feature]) + "/"
        zmax = np.ndarray.max(node_info[:,:,:,feature])
        zmin = np.ndarray.min(node_info[:,:,:,feature])
        for file in range(num_files):
            xydata = node_info[file,:,:,feature]
            #TODO: vim/vmax in norm of outside of it?
            plt.matshow(xydata, cmap=plt.get_cmap('plasma'), origin="lower", vmin=zmin, vmax=zmax) #norm=matplotlib.colors.LogNorm())
            #plt.autoscale()
            plt.ylabel("Benefits")
            plt.xlabel("Damages")
            plt.title(str(header[feature]) + " of Each BD Pair")
            plt.colorbar()
            plt.savefig(dirr + str(iters[file]) + ".png")
            plt.clf()
            plt.cla()
            plt.close()
    # FOLLOWING PLOTS ARE DEPENDENT ON PARTICULAR FEATURES & THEIR POSITIONS
    # ['freq', 'freq in solution', 'leaf', 'hub', 'fitness']

    # leaf*freq
    dirr = output_dir + "node_plots/LeafContrib/"
    zmax = np.ndarray.max(node_info[:,:,:,0]*node_info[:,:,:,2])
    zmin = np.ndarray.min(node_info[:,:,:,0]*node_info[:,:,:,2])

    for file in range(num_files):
        xydata = node_info[file,:,:,0]*node_info[file,:,:,2]

        plt.matshow(xydata, cmap=plt.get_cmap('plasma'), origin="lower", vmin=zmin, vmax=zmax)
        plt.ylabel("Benefits")
        plt.xlabel("Damages")
        plt.title("Contribution to Leaf Fitness of Each BD Pair")
        plt.colorbar()
        plt.savefig(dirr + str(iters[file]) + ".png")
        plt.clf()
        plt.cla()
        plt.close()

    # hub*freq_in_soln
    dirr = output_dir + "node_plots/HubContrib/"
    zmax = np.ndarray.max(node_info[:,:,:,1] * node_info[:,:,:,3])
    zmin = np.ndarray.min(node_info[:,:,:,1] * node_info[:,:,:,3])

    for file in range(num_files):
        xydata = node_info[file,:,:,1] * node_info[file,:,:,3]

        plt.matshow(xydata, cmap=plt.get_cmap('plasma'), origin="lower", vmin=zmin, vmax=zmax)
        plt.ylabel("Benefits")
        plt.xlabel("Damages")
        plt.title("Contribution to Hub Fitness of Each BD Pair")
        plt.colorbar()
        plt.savefig(dirr + str(iters[file]) + ".png")
        plt.clf()
        plt.cla()
        plt.close()

    # leaf*freq + hub*freq_in_soln
    dirr = output_dir + "node_plots/Fitness_Frequency/"
    zmax = np.ndarray.max(node_info[:,:,:,0] * node_info[:,:,:,2] + node_info[:,:,:,1] * node_info[:,:,:,3])
    zmin = np.ndarray.min(node_info[:,:,:,0] * node_info[:,:,:,2] + node_info[:,:,:,1] * node_info[:,:,:,3])

    for file in range(num_files):
        xydata = (node_info[file,:,:,0] * node_info[file,:,:,2] + node_info[file,:,:,1] * node_info[file,:,:,3])
        plt.matshow(xydata, cmap=plt.get_cmap('plasma'), origin="lower", vmin=zmin, vmax=zmax)
        plt.ylabel("Benefits")
        plt.xlabel("Damages")
        plt.title("Contribution to Fitness of Each BD Pair")
        plt.colorbar()
        plt.savefig(dirr + str(iters[file]) + ".png")
        plt.clf()
        plt.cla()
        plt.close()






def check_dirs(dirr, header):

    if not os.path.exists(dirr + "/node_plots/"):
        os.makedirs(dirr + "/node_plots/")

    for i in range(len(header)):
        if not os.path.exists(dirr + "/node_plots/" + str(header[i])):
            os.makedirs(dirr + "/node_plots/" + str(header[i]))

    if not os.path.exists(dirr + "/node_plots/LeafContrib/"):
        os.makedirs(dirr + "/node_plots/LeafContrib/")
    if not os.path.exists(dirr + "/node_plots/HubContrib/"):
        os.makedirs(dirr + "/node_plots/HubContrib/")
    if not os.path.exists(dirr + "/node_plots/Fitness_Frequency/"):
        os.makedirs(dirr + "/node_plots/Fitness_Frequency/")

