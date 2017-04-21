import matplotlib
matplotlib.use('Agg') # you need this line if you're running this code on rupert
import sys, os, matplotlib.pyplot as plt, matplotlib.patches as mpatches, networkx as nx, numpy as np
import math
#from scipy.stats import itemfreq
import matplotlib.ticker as ticker
import random as rd
#from ticker import FuncFormatter

def plot_em(real_net_file, sim_net_file, plot_title):
    # each line in 'input.txt' should be: [network name (spaces allowed) followed by /path/to/edge/file.txt/or/pickled/network.dump]
    input_files = open(real_net_file,'r').readlines()

    colors = ['#E6FAB3', '#B3FAE2', '#B2C6FB','#E4B2FB','#FBB2B2','#F9C140','#D2F940']
    # pick more colors from here: http://htmlcolorcodes.com/ , number of colos >= number of networks in input_files ]
    i = 0
    for  line in input_files:
        H = []
        sim_net = nx.read_edgelist(sim_net_file, nodetype=int, create_using=nx.DiGraph())
        #print("Simulated Net: \tnodes " + str(len(M.nodes())) + "\tedges " + str(len(M.edges())))
        num_nodes = len(sim_net.nodes())


        # PLOT REAL NETS
        line         = line.strip()
        title        = line.split()[:-1][0]
        network_file = line.split()[-1]

        # if networks are edge files, load them using load_network(), if they're pickled (faster) load them using nx's read_gpickle
        #M = init.load_network ({'network_file':network_file.strip(), 'biased':False})
        #M = nx.read_edgelist(network_file.strip(),nodetype=int,create_using=nx.DiGraph())
        #nx.write_gpickle(M,'dumps/'+network_file.split('/')[-1].split('.')[0]+'.dump')
        M = nx.read_gpickle(network_file)

        repeats = 100
        for j in range(repeats):
            sample_nodes = rd.sample(M.nodes(), num_nodes)

            #with open (network_file,''
            #print (network_file.split('/')[-1].strip()+"\tnodes "+str(len(M.nodes()))+"\tedges "+str(len(M.edges())))

            degrees = list(M.degree(sample_nodes).values())
            in_degrees, out_degrees = list(M.in_degree(sample_nodes).values()), list(M.out_degree(sample_nodes).values())
            #degrees = in_degrees + out_degrees

            #NP GET FREQS
            degs, freqs = np.unique(degrees, return_counts=True)
            tot = float(sum(freqs))
            freqs = [(f/tot)*100 for f in freqs]

            plt.loglog(degs, freqs, basex=10, basey=10, linestyle='-',  linewidth=2, color = colors[i], alpha=0.2, markersize=8, marker='', markeredgecolor='None')
            # you can also scatter the in/out degrees on the same plot
            # plt.scatter( .... )


        #i think one patch per set of samples?
        patch =  mpatches.Patch(color=colors[i], label=title)

        H = H + [patch]

        #PLOT SIM NET
        degrees = list(sim_net.degree().values())
        in_degrees, out_degrees = list(sim_net.in_degree().values()), list(sim_net.out_degree().values())
        # degrees = in_degrees + out_degrees
        degs, freqs = np.unique(degrees, return_counts=True)
        tot = float(sum(freqs))
        freqs = [(f / tot) * 100 for f in freqs]

        plt.loglog(degs, freqs, basex=10, basey=10, linestyle='-', linewidth=2, color='#000000', alpha=1,
                   markersize=8, marker='', markeredgecolor='None')

        patch = mpatches.Patch(color=colors[i], label="Simulation")

        H = H + [patch]


        #FORMAT PLOT
        ax = plt.gca() # gca = get current axes instance

        # if you are plotting a single network, you can add a text describing the fitness function used:
        ax.text(.5,.7,r'$f(N)=\prod\frac {b}{b+d}\times\sum_{j=1}^{n} etc$', horizontalalignment='center', transform=ax.transAxes, size=20)
        # change (x,y)=(.5, .7) to position the text in a good location; the "f(N)=\sum \frac{}" is a mathematical expression using latex, see this:
        # https://www.sharelatex.com/learn/Mathematical_expressions
        # http://matplotlib.org/users/usetex.html

        ax.set_xlim([0.7,200])
        ax.set_ylim([.1,100])

        xfmatter = ticker.FuncFormatter(LogXformatter)
        yfmatter = ticker.FuncFormatter(LogYformatter)
        ax.get_xaxis().set_major_formatter(xfmatter)
        ax.get_yaxis().set_major_formatter(yfmatter)

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.tick_params(axis='both', which='both', right='off', top='off') #http://matplotlib.org/api/axes_api.html#matplotlib.axes.Axes.tick_params
        plt.legend(loc='upper right', handles=H, frameon=False,fontsize= 11)
        plt.xlabel('degree  ')
        plt.ylabel('% genes ')
        plt.title('Degree Distribution of ' + str(title) + ' vs Simulation')

        plt.tight_layout()
        plt.savefig(str(plot_title) + " vs " + str(title) + ".png", dpi=300,bbox='tight') # http://matplotlib.org/api/figure_api.html#matplotlib.figure.Figure.savefig
        plt.clf()
        plt.cla()
        plt.close()

    i += 1

def walklevel(some_dir, level=1): #MOD to dirs only
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir):
        yield dirs
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]



###################################################
def LogYformatter(y, _):
    if int(y) == float(y) and float(y)>0:
        return str(int(y))+' %'
    elif float(y) >= .1:
        return str(y)+' %'
    else:
        return ""
###################################################
def LogXformatter(x, _):
    if x<=1:
        return str(int(x))
    if math.log10(x)  == int(math.log10(x)):
        return str(int(x))
    else:
        return ""
######################################################

if __name__ == "__main__":
    base_dir = "/home/2014/choppe1/Documents/EvoNet/virt_workspace/data/output/"
    real_net_file = "/home/2014/choppe1/Documents/EvoNet/virt_workspace/data/input/input_nets.txt"

    if (str(sys.argv[1]) == 'single'):
        sim_dirr = str(base_dir + sys.argv[2])
        if not os.path.exists(sim_dirr + "/comparison_plots/"):
            os.makedirs(sim_dirr + "/comparison_plots/")
        for sim_file in os.listdir(sim_dirr+"/nets/"):
            print("Plotting sim file " + str(sim_file))
            plot_em(real_net_file, sim_dirr +"/nets/"+ sim_file, sim_dirr + "/comparison_plots/" + sim_file)

    else:
        sim_dirr = str(base_dir + sys.argv[1])

        sims = list(walklevel(sim_dirr)) 
        for sim in sims[0]:
            sim = sim_dirr + "/" + sim
            print("\n\nPlotting from sim dir " + str(sim))
            if not os.path.exists(sim + "/comparison_plots/"):
                os.makedirs(sim + "/comparison_plots/")
            for sim_file in os.listdir(sim+"/nets/"):
                print("Plotting sim file " + str(sim_file))
                plot_em(real_net_file, sim +"/nets/"+ sim_file, sim + "/comparison_plots/" + sim_file)
    print("\nDone.\n")
