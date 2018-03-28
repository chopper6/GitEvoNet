import matplotlib
matplotlib.use('Agg') # you need this line if you're running this code on rupert
import sys, os, matplotlib.pyplot as plt, matplotlib.patches as mpatches, networkx as nx, numpy as np
import math, re, pickle


def plot_dir(output_dir, biased, bias_on):
    dirs = ["/undirected_degree_distribution/", "/undirected_degree_distribution/loglog/", "/undirected_degree_distribution/loglog%/", "/undirected_degree_distribution/scatter/", "/undirected_degree_distribution/scatter%/"]
    for dirr in dirs:
        if not os.path.exists(output_dir + dirr):
            os.makedirs(output_dir + dirr)

    for root, dirs, files in os.walk(output_dir + "/nets/"):
        for f in files:
            print("plot_dir(): file " + str(f))
            undir_deg_distrib(root + "/" + f, output_dir + "/undirected_degree_distribution/", f, biased, bias_on)


def undir_deg_distrib(net_file, destin_path, title, biased, bias_on):
    print('undir_deg_distrib: biased=' + str(biased) + ', bias_on=' + str(bias_on))

    if (re.match(re.compile("[a-zA-Z0-9]*pickle"), net_file)):
        with open(net_file, 'rb') as file:
            net = pickle.load(file)
            file.close()
    else:
        net = nx.read_edgelist(net_file, nodetype=int, create_using=nx.DiGraph())

    colors = ['#0099cc','#ff5050', '#6699ff']
    color_choice = colors[0]

    for type in ['loglog', 'loglog%', 'scatter', 'scatter%']:
        H = []
        #loglog
        degrees = list(net.degree().values())
        degs, freqs = np.unique(degrees, return_counts=True)
        tot = float(sum(freqs))
        if (type=='loglog%' or type=='scatter%'): freqs = [(f/tot)*100 for f in freqs]

        #derive vals from conservation scores
        consv_vals, ngh_consv_vals = [], []
        if (biased == True or biased == 'True'):
            for deg in degs: #deg consv is normalized by num nodes
                avg_consv, ngh_consv, num_nodes = 0,0,0
                for node in net.nodes():
                    if (net.degree(node) == deg):
                        if (bias_on == 'nodes'):
                            avg_consv += abs(.5-net.node[node]['conservation_score'])

                            avg_ngh_consv = 0
                            for ngh in net.neighbors(node):
                                avg_ngh_consv += net.node[ngh]['conservation_score']
                            avg_ngh_consv /= len(net.neighbors(node))
                            ngh_consv += abs(.5-avg_ngh_consv)

                        elif (bias_on == 'edges'): #node consv is normalized by num edges
                            node_consv, num_edges = 0, 0
                            for edge in net.edges(node):
                                node_consv += net[edge[0]][edge[1]]['conservation_score']
                                num_edges += 1
                            if (num_edges != 0): node_consv /= num_edges
                        num_nodes += 1
                avg_consv /= num_nodes
                ngh_consv /= num_nodes
                consv_vals.append(avg_consv)
                ngh_consv_vals.append(ngh_consv)
            assert(len(consv_vals) == len(degs))

            with open(destin_path + "/degs_freqs_bias_nghBias",'wb') as file:
                pickle.dump(file, [degs, freqs, consv_vals, ngh_consv_vals])


            cmap = plt.get_cmap('plasma')
            consv_colors = cmap(consv_vals)

            if (type == 'loglog' or type=='loglog%'): plt.loglog(degs, freqs, basex=10, basey=10, linestyle='',  linewidth=2, c = consv_colors, alpha=1, markersize=8, marker='D', markeredgecolor='None')
            elif (type == 'scatter' or type=='scatter%'):
                sizes = [10 for i in range(len(degs))]
                plt.scatter(degs, freqs, c = consv_colors, alpha=1, s=sizes, marker='D')

        else:
            if (type == 'loglog' or type=='loglog%'): plt.loglog(degs, freqs, basex=10, basey=10, linestyle='',  linewidth=2, color = color_choice, alpha=1, markersize=8, marker='D', markeredgecolor='None')
            elif (type == 'scatter' or type=='scatter%'):
                sizes = [10 for i in range(len(degs))]
                plt.scatter(degs, freqs, color = color_choice, alpha=1, s=sizes, marker='D')
        patch =  mpatches.Patch(color=color_choice, label=title + "_" + type)
        H = H + [patch]

        #FORMAT PLOT
        ax = plt.gca() # gca = get current axes instance

        if (type == 'loglog%' or type=='scatter%'):
            ax.set_xlim([0,100])
            ax.set_ylim([0,100])
        elif (type == 'loglog' or type == 'scatter'):
            max_x = max(1,math.floor(max(degs)/10))
            max_x = max_x*10+10

            max_y = max(1,math.floor(max(freqs)/10))
            max_y = max_y*10+100

            upper_lim = max(max_x, max_y)

            ax.set_xlim([0, upper_lim])
            ax.set_ylim([0, upper_lim])

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.tick_params(axis='both', which='both', right='off', top='off') #http://matplotlib.org/api/axes_api.html#matplotlib.axes.Axes.tick_params
        plt.legend(loc='upper right', handles=H, frameon=False,fontsize= 11)
        plt.xlabel('Degree')
        if (type=='loglog%'): plt.ylabel('Percent of Nodes with Given Degree')
        else: plt.ylabel('Number of Nodes with Given Degree')
        #plt.title('Degree Distribution of ' + str(title) + ' vs Simulation')

        plt.tight_layout()
        plt.savefig(destin_path + "/" + type + "/" + title + ".png", dpi=300,bbox='tight') # http://matplotlib.org/api/figure_api.html#matplotlib.figure.Figure.savefig
        plt.clf()
        plt.cla()
        plt.close()


if __name__ == "__main__":
    base_dir = "/home/2014/choppe1/Documents/EvoNet/virt_workspace/data/output/" #customize for curr work
    real_net_file = "/home/2014/choppe1/Documents/EvoNet/virt_workspace/data/input/input_all_nets.txt" #check this is still on yamaska

    if sys.argv[1] == 'comparison':
        net1_path = sys.argv[2]
        net2_path = sys.argv[3]
        biased = False  # sys.argv[2]
        bias_on = None  # sys.argv[3]

        dirs = ["/undirected_degree_distribution/", "/undirected_degree_distribution/loglog/",
                "/undirected_degree_distribution/loglog%/", "/undirected_degree_distribution/scatter/",
                "/undirected_degree_distribution/scatter%/"]
        for dirr in dirs:
            if not os.path.exists(net1_path + dirr):
                os.makedirs(net1_path + dirr)

    if sys.argv[1] == 'biased':
        biased = True
        bias_on = sys.argv[2]
        parent_dir = sys.argv[3]

        for dirr in sys.argv[4:]:
            print("plotting " + base_dir + parent_dir + dirr)
            plot_dir(base_dir + parent_dir + dirr, biased, bias_on)

    else:
        biased = None
        bias_on = None

        parent_dir = sys.argv[1]

        for dirr in sys.argv[2:]:
            print("plotting " + base_dir + parent_dir + dirr)
            plot_dir(base_dir + parent_dir + dirr, biased, bias_on)

    print("\nDone.\n")
