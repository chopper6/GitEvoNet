import matplotlib
matplotlib.use('Agg') # you need this line if you're running this code on rupert
import sys, os, matplotlib.pyplot as plt, matplotlib.patches as mpatches, networkx as nx, numpy as np
import math
#from scipy.stats import itemfreq
import matplotlib.ticker as ticker
import matplotlib.font_manager as font_manager
from matplotlib import rcParams
import random as rd


def plot_dir(output_dir, biased, bias_on):
    if not os.path.exists(output_dir + "/undirected_degree_distribution/"):
        os.makedirs(output_dir+"/undirected_degree_distribution/")
    #files = os.walk(output_dir + "/nets/")
    for root, dirs, files in os.walk(output_dir + "/nets/"):
        for f in files:
            print("plot_dir(): file " + str(f))
            undir_deg_distrib(root + "/" + f, output_dir + "/undirected_degree_distribution/", f, biased, bias_on)


def undir_deg_distrib(net_file, destin_path, title, biased, bias_on):
    print('undir_deg_distrib: biased=' + str(biased) + ', bias_on=' + str(bias_on))
    #update_rcParams()
    # each line in 'input.txt' should be: [network name (spaces allowed) followed by /path/to/edge/file.txt/or/pickled/network.dump]

    net = nx.read_edgelist(net_file, nodetype=int, create_using=nx.DiGraph())

    colors = ['#0099cc','#ff5050', '#6699ff']
    color_choice = colors[0]

    for type in ['loglog', 'scatter']:
        H = []
        #loglog
        degrees = list(net.degree().values())
        degs, freqs = np.unique(degrees, return_counts=True)
        tot = float(sum(freqs))
        freqs = [(f/tot)*100 for f in freqs]



        #derive vals from conservation scores
        consv_vals = []
        if (biased == True or biased == 'True'):
            print('using bias')
            for deg in degs: #deg consv is normalized by num nodes
                avg_consv, num_nodes = 0,0
                for node in net.nodes():
                    if (net.degree(node) == deg):
                        if (bias_on == 'nodes'):
                            avg_consv += net.node[node]['conservation_score']
                        elif (bias_on == 'edges'): #node consv is normalized by num edges
                            node_consv, num_edges = 0, 0
                            for edge in net.edges(node):
                                node_consv += net[edge[0]][edge[1]]['conservation_score']
                                num_edges += 1
                            if (num_edges != 0): node_consv /= num_edges
                        num_nodes += 1
                avg_consv /= num_nodes
                consv_vals.append(avg_consv)
            assert(len(consv_vals) == len(degs))
            cmap = plt.get_cmap('plasma')
            consv_colors = cmap(consv_vals)

            if (type == 'loglog'): plt.loglog(degs, freqs, basex=10, basey=10, linestyle='',  linewidth=2, c = consv_colors, alpha=1, markersize=8, marker='D', markeredgecolor='None')
            elif (type == 'scatter'):
                sizes = [10 for i in range(len(degs))]
                plt.scatter(degs, freqs, c = consv_colors, alpha=1, s=sizes, marker='D')

        else:
            if (type == 'loglog'): plt.loglog(degs, freqs, basex=10, basey=10, linestyle='',  linewidth=2, color = color_choice, alpha=1, markersize=8, marker='D', markeredgecolor='None')
            elif (type == 'scatter'):
                sizes = [10 for i in range(len(degs))]
                plt.scatter(degs, freqs, color = color_choice, alpha=1, s=sizes, marker='D')
        patch =  mpatches.Patch(color=color_choice, label=title + "_" + type)
        H = H + [patch]

        #FORMAT PLOT
        ax = plt.gca() # gca = get current axes instance

        ax.set_xlim([0,1000])
        ax.set_ylim([0,1000])

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.tick_params(axis='both', which='both', right='off', top='off') #http://matplotlib.org/api/axes_api.html#matplotlib.axes.Axes.tick_params
        plt.legend(loc='upper right', handles=H, frameon=False,fontsize= 11)
        plt.xlabel('Degree')
        plt.ylabel('Number of Nodes with Given Degree')
        #plt.title('Degree Distribution of ' + str(title) + ' vs Simulation')

        plt.tight_layout()
        plt.savefig(destin_path + title + "_" + type + ".png", dpi=300,bbox='tight') # http://matplotlib.org/api/figure_api.html#matplotlib.figure.Figure.savefig
        plt.clf()
        plt.cla()
        plt.close()




if __name__ == "__main__":
    base_dir = "/home/2014/choppe1/Documents/EvoNet/virt_workspace/data/output/entropy2_again/" #customize for curr work
    real_net_file = "/home/2014/choppe1/Documents/EvoNet/virt_workspace/data/input/input_all_nets.txt" #check this is still on yamaska

    biased = False #sys.argv[2]
    bias_on = None #sys.argv[3]
    for dirr in sys.argv[1:]:
        print("plotting " + base_dir + dirr)
        plot_dir(base_dir + dirr, biased, bias_on)

    print("\nDone.\n")
