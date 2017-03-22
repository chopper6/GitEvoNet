import matplotlib, os, math, sys
matplotlib.use('Agg') # This must be done before importing matplotlib.pyplot
import matplotlib.pyplot as plt
import node_fitness, slices_helper, bar2d
import numpy as np


def all_fitness_plots(output_dir):
    # might want to normalize by # pressurize rounds
    if not os.path.exists(output_dir + "node_info/"):
        print("ERROR in plot_fitness: no directory to read in from, missing /node_info/.")
    node_info, iters, header = node_fitness.read_in(output_dir + "node_info/")
    # [file, B, D, features]
    check_dirs(output_dir, header)

    #bar2d_plots(output_dir, node_info)
    BD_pairs(output_dir, node_info, iters, header)  #MUST COME 2nd SINCE NORMLZ NODE_INFO VALS



def just_for_hubfreqcontrib(node_info):
    for i in range(len(node_info)):
        for j in range(len(node_info[i])):
            for k in range(len(node_info[i][j])):
                node_info[i, j, k, 3] *= node_info[i, j, k, 1]
                
    return node_info



def BD_pairs(output_dir, node_info, iters, header):
    #node_info = just_for_hubfreqcontrib(node_info)
    num_features = len(header)
    node_info = fraction_normz(node_info)
    node_info = log_scale(node_info)

    num_files = len(node_info)
    max_B = len(node_info[0])
    # single feature plots

    #header[3] = "Contribution to Hub Fitness"

    for feature in range(num_features):
        dirr = output_dir + "node_plots/" + str(header[feature]) + "/"
        zmax = np.ndarray.max(node_info[:,:,:,feature])
        zmin = np.ndarray.min(node_info[:,:,:,feature])
        for file in range(num_files):
            xydata = node_info[file,:,:,feature]
            #TODO: vim/vmax in norm of outside of it?
            plt.matshow(xydata, cmap=plt.get_cmap('plasma'), origin="lower", vmin=zmin, vmax=zmax)  #, norm=matplotlib.colors.LogNorm())
            #plt.autoscale()
            plt.ylabel("Benefits", fontsize=15)
            plt.xlabel("Damages", fontsize=15)
            #plt.title(str(header[feature]), fontsize=20)
            cbar = plt.colorbar(label=str(header[feature]))
            #cbar.set_ticks([0,zmax/4, zmax/2,3*zmax/4 , zmax])
            #maxx =  math.ceil(np.ndarray.max(node_info_fractions[:,:,:,feature]))*10
            #cbar.set_ticklabels([0,maxx/1000, maxx/100, maxx/10, maxx])
            #plt.xaxis.set_ticks_position('bottom')
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
        plt.ylabel("Benefits", fontsize=15)
        plt.xlabel("Damages", fontsize=15)
        #plt.title("Contribution to Leaf Fitness", fontsize=25)
        cbar = plt.colorbar(label="Percent " + str(header[feature]))
        cbar.set_ticks([0,zmax/4, zmax/2,3*zmax/4 , zmax])
        cbar.set_ticklabels([0,1/10, 1, 10, 100])
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
        plt.ylabel("Benefits", fontsize=15)
        plt.xlabel("Damages", fontsize=15)
        #plt.title("Contribution to Hub Fitness", fontsize=25)
        cbar = plt.colorbar(label="Percent " + str(header[feature]))
        #cbar.set_ticks([0,zmax/4, zmax/2,3*zmax/4 , zmax])
        #cbar.set_ticklabels([0,1/10, 1, 10, 100])
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
        plt.ylabel("Benefits", fontsize=15)
        plt.xlabel("Damages", fontsize=15)
        #plt.title("Contribution to Fitness", fontsize=25)
        cbar = plt.colorbar(label="Percent " + str(header[feature]))
        cbar.set_ticks([0,zmax/4, zmax/2,3*zmax/4 , zmax])
        cbar.set_ticklabels([0,1/10, 1, 10, 100])
        plt.savefig(dirr + str(iters[file]) + ".png")
        plt.clf()
        plt.cla()
        plt.close()




def bar2d_plots(output_dir, node_info):
    slices = slices_helper.fill_slices(node_info)
    #print(slices)
    bar2d.plot_bar2d(output_dir, "Start", slices[0])
    bar2d.plot_bar2d(output_dir, "End", slices[1])

def fraction_normz (node_info):
    # only occurs with freq and freq in soln
    # [file, B, D, features]
    num_features = (len(node_info[0][0][0]))

    maxx = [[1 for l in range(num_features)] for i in range(len(node_info))]
    for i in range(len(node_info)):
        for l in range(num_features):
            maxx[i][l] =  np.max(node_info[i,:,:,l])


    for i in range(len(node_info)):
        for j in range(len(node_info[i])):
            for k in range(len(node_info[i][j])):
                for l in [0,1,3]:
                    if (node_info[i, j, k, l] != 0): node_info[i,j,k,l] = (node_info[i,j,k,l] / maxx[i][l])*100


    return node_info

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
    if not os.path.exists(dirr + "/node_plots/Contribution to Hub Fitness/"):
        os.makedirs(dirr + "/node_plots/Contribution to Hub Fitness/")



def log_scale (node_info):
    # [file, B, D, features]
    num_features = (len(node_info[0][0][0]))

    for i in range(len(node_info)):
        for j in range(len(node_info[i])):
            for k in range(len(node_info[i][j])):
                for l in [0,1,3]: #range(len(node_info[i][j][k])):
                    if (node_info[i, j, k, l] != 0): node_info[i,j,k,l] = math.log10(node_info[i,j,k,l])

    mins = [None for i in range(num_features)]
    for feature in range(num_features):
        mins[feature] = np.ndarray.min(node_info[:, :, :, feature])
        if (mins[feature] > 0): print ("WARNING: plot_fitness.log_scale(): min is > 0 after scaling: min= " + str(mins[feature]))

    
    for i in range(len(node_info)):
        for j in range(len(node_info[i])):
            for k in range(len(node_info[i][j])):
                for l in [0,1,3]: #range(len(node_info[i][j][k])):
                    if (node_info[i, j, k, l] != 0): node_info[i, j, k, l] += -1*(mins[l])
    
    return node_info


def simple_example(dirr):
    node_info = [[[[0 for i in range(5)] for j in range(4)] for k in range(4)] for m in range(2)]
    node_info = np.array(node_info)
    # node 0
    node_info[0][2][0][0] = 1
    node_info[0][2][0][1] = 1
    node_info[0][2][0][3] = 1

    # node 1
    node_info[0][3][3][0] = 1

    # node 2
    node_info[0][0][1][0] = 1

    # node 3
    node_info[0][2][1][0] = 1
    node_info[0][2][1][1] = 1
    node_info[0][2][1][3] = 1

    # node 4
    node_info[0][3][1][0] = 1
    node_info[0][3][1][1] = 1
    node_info[0][3][1][3] = 3

    BD_pairs(dirr, node_info, [0,1], ["Freq", "Freq in Solution", "Leaf[empty]", "Hub", "Fitness[empty]"])
    slices = slices_helper.fill_slices(node_info)
    bar2d.plot_bar2d(dirr, "Start", slices[0])
    print("Finished first set of bar plots\n")
    bar2d.plot_bar2d(dirr, "End", slices[1])



if __name__ == "__main__":
    #first bash arg should be parent directory, then each child directory
    dirr_base = "/home/2014/choppe1/Documents/EvoNet/virt_workspace/data/output/"

    if (sys.argv[1] == "simpleEx"):
        simple_example(dirr_base+ "/simpleEx/")

    dirr_parent = sys.argv[1]
    dirr_base += dirr_parent

    for arg in sys.argv[2:]:
        print("Plotting dirr " + str(arg))
        dirr_addon = arg
        dirr= dirr_base + dirr_addon + "/"
        all_fitness_plots(dirr)

    print("Finished plotting BD pairs.")
