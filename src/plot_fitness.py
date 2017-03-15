import matplotlib, os, math, sys
matplotlib.use('Agg') # This must be done before importing matplotlib.pyplot
import matplotlib.pyplot as plt
import node_fitness
import numpy as np

def BD_pairs(output_dir):
    # might want to normalize by # pressurize rounds
    if not os.path.exists(output_dir + "/node_info/"):
        print("ERROR in plot_fitness: no directory to read in from, missing /node_info/.")
        return 1
    node_info, iters, header = node_fitness.read_in(output_dir + "/node_info/")
    # [file, B, D, features]
    node_info = log_scale(node_info)

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
            plt.title(str(header[feature]))
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
        plt.title("Contribution to Leaf Fitness")
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
        plt.title("Contribution to Hub Fitness")
        plt.colorbar()
        plt.savefig(dirr + str(iters[file]) + ".png")
        plt.clf()
        plt.cla()
        plt.close()

    # leaf*freq + hub*freq_in_soln
    dirr = output_dir + "node_plots/FitnessContrib/"
    zmax = np.ndarray.max(node_info[:,:,:,0] * node_info[:,:,:,2] + node_info[:,:,:,1] * node_info[:,:,:,3])
    zmin = np.ndarray.min(node_info[:,:,:,0] * node_info[:,:,:,2] + node_info[:,:,:,1] * node_info[:,:,:,3])

    for file in range(num_files):
        xydata = (node_info[file,:,:,0] * node_info[file,:,:,2] + node_info[file,:,:,1] * node_info[file,:,:,3])
        plt.matshow(xydata, cmap=plt.get_cmap('plasma'), origin="lower", vmin=zmin, vmax=zmax)
        plt.ylabel("Benefits")
        plt.xlabel("Damages")
        plt.title("Contribution to Fitness")
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
    if not os.path.exists(dirr + "/node_plots/FitnessContrib/"):
        os.makedirs(dirr + "/node_plots/FitnessContrib/")




def log_scale (node_info):
    # [file, B, D, features]
    num_features = (len(node_info[0][0][0]))

    for i in range(len(node_info)):
        for j in range(len(node_info[i])):
            for k in range(len(node_info[i][j])):
                for l in range(len(node_info[i][j][k])):
                    if (i==10 and j==0 and k==1 and l==2): print("log_scale(): leaf 0,1 in file 10 = " + str(node_info[i,j,k,l]))
                    if (i==0 and j==0 and k==1 and l==2): print("log_scale(): leaf 0,1 in file 0 = " + str(node_info[i,j,k,l]))
                    if (node_info[i,j,k,l] != 0): 
                        node_info[i,j,k,l] = math.log10(node_info[i,j,k,l])
                    if (i==10 and j==0 and k==1 and l==2): print("log_scale(): leaf 0,1 in file 10 = " + str(node_info[i,j,k,l]))
                    if (i==0 and j==0 and k==1 and l==2): print("log_scale(): leaf 0,1 in file 0 = " + str(node_info[i,j,k,l]))
    mins = [None for i in range(num_features)]
    for feature in range(num_features):
        mins[feature] = np.ndarray.min(node_info[:,:,:,feature])
        if (mins[feature] > 0): print ("WARNING: plot_fitness.log_scale(): min is > 0 after scaling: min= " + str(mins[feature]))
        if (feature==2): print("log_scale(): leaf min = " + str(mins[feature]))

    for i in range(len(node_info)):
        for j in range(len(node_info[i])):
            for k in range(len(node_info[i][j])):
                for l in range(len(node_info[i][j][k])):
                   if (node_info[i,j,k,l] != 0): node_info[i, j, k, l] += -1*(mins[l])
                   if (i==10 and j==0 and k==1 and l==2): print("log_scale(): leaf 0,1 in file 10 = " + str(node_info[i,j,k,l]))
                   if (i==0 and j==0 and k==1 and l==2): print("log_scale(): leaf 0,1 in file 0 = " + str(node_info[i,j,k,l]))
    return node_info



if __name__ == "__main__":
    #first bash arg should be parent directory, then each child directory
    dirr_base = "/home/2014/choppe1/Documents/EvoNet/virt_workspace/data/output/"
    dirr_parent = sys.argv[1]
    dirr_base += dirr_parent

    for arg in sys.argv[2:]:
        print("Plotting dirr " + str(arg))
        dirr_addon = arg
        dirr= dirr_base + dirr_addon + "/"
        BD_pairs(dirr)

    print("Finished plotting BD pairs.")
