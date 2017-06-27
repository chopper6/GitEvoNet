import matplotlib
matplotlib.use('Agg') # you need this line if you're running this code on rupert
import sys, os, matplotlib.pyplot as plt, matplotlib.patches as mpatches, networkx as nx, numpy as np
import math
#from scipy.stats import itemfreq
import matplotlib.ticker as ticker
import matplotlib.font_manager as font_manager
from matplotlib import rcParams
import random as rd
#from ticker import FuncFormatter

def plot_pairs(real_net_file, real_net_name, sim_net_file, plot_title):
    input_files = open(real_net_file,'r').readlines()

    colors = ['#ADECD7', '#ADC0F3','#E4B2FB','#FBB2B2','#FFCC66','#C3F708']
    i=0
    for line in input_files:
        name, network_file = line.strip().split(' ')
        if (name==real_net_name or real_net_name == 'all'):
            H = []
            sim_net = nx.read_edgelist(sim_net_file, nodetype=int, create_using=nx.DiGraph())
            # print("Simulated Net: \tnodes " + str(len(M.nodes())) + "\tedges " + str(len(M.edges())))
            sim_nodes = sim_net.nodes()

            # PLOT REAL NETS
            title = plot_title + "_" + str(name)

            # M = init.load_network ({'network_file':network_file.strip(), 'biased':False})
            # M = nx.read_edgelist(network_file.strip(),nodetype=int,create_using=nx.DiGraph())
            real_net = nx.read_gpickle(network_file)


            real_nodes = real_net.nodes()
            if (len(real_nodes) != len(sim_nodes)): print("WARNING: real net does not have same number of nodes as simulation.")
            if (len(real_net.edges()) != len(sim_net.edges())): print("WARNING: real net does not have same number of edges as simulation.")

            # if (j==0): print(title + " has ENR = " + str(len(M.edges())/float(len(M.nodes()))) + ".\n")
            # with open (network_file,''
            # print (network_file.split('/')[-1].strip()+"\tnodes "+str(len(M.nodes()))+"\tedges "+str(len(M.edges())))

            degrees = list(real_net.degree().values())
            #in_degrees, out_degrees = list(M.in_degree(sample_nodes).values()), list(M.out_degree(sample_nodes).values())
            # degrees = in_degrees + out_degrees

            # NP GET FREQS
            # TODO: is % normz still nec? mmight be more astethic
            degs, freqs = np.unique(degrees, return_counts=True)
            tot = float(sum(freqs))
            freqs = [(f / tot) * 100 for f in freqs]

            plt.loglog(degs, freqs, basex=10, basey=10, linestyle='', linewidth=1, color=colors[i], alpha=1, markersize=10, marker='.', markeredgecolor='None', )
            # you can also scatter the in/out degrees on the same plot
            # plt.scatter( .... )

            # i think one patch per set of samples?
            patch = mpatches.Patch(color=colors[i], label=title)

            H = H + [patch]

            # PLOT SIM NET
            degrees = list(sim_net.degree().values())
            #in_degrees, out_degrees = list(sim_net.in_degree().values()), list(sim_net.out_degree().values())
            # degrees = in_degrees + out_degrees
            degs, freqs = np.unique(degrees, return_counts=True)
            tot = float(sum(freqs))
            freqs = [(f / tot) * 100 for f in freqs]

            plt.loglog(degs, freqs, basex=10, basey=10, linestyle='', linewidth=1, color='#000000', alpha=1, markersize=10, marker='.', markeredgecolor='None')

            patch = mpatches.Patch(color='#000000', label="Simulation")

            H = H + [patch]

            # FORMAT PLOT
            ax = plt.gca()  # gca = get current axes instance

            # if you are plotting a single network, you can add a text describing the fitness function used:
            # ax.text(.5,.7,r'$f(N)=\prod\frac {b}{b+d}\times\sum_{j=1}^{n} etc$', horizontalalignment='center', transform=ax.transAxes, size=20)
            # change (x,y)=(.5, .7) to position the text in a good location; the "f(N)=\sum \frac{}" is a mathematical expression using latex, see this:
            # https://www.sharelatex.com/learn/Mathematical_expressions
            # http://matplotlib.org/users/usetex.html

            # ax.set_xscale('log')
            # ax.set_yscale('log')
            ax.set_xlim([0.7, 200]) #TODO: change these?
            ax.set_ylim([.1, 100])

            xfmatter = ticker.FuncFormatter(LogXformatter)
            yfmatter = ticker.FuncFormatter(LogYformatter)
            ax.get_xaxis().set_major_formatter(xfmatter)
            ax.get_yaxis().set_major_formatter(yfmatter)

            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            plt.tick_params(axis='both', which='both', right='off',
                            top='off')  # http://matplotlib.org/api/axes_api.html#matplotlib.axes.Axes.tick_params
            plt.legend(loc='upper right', handles=H, frameon=False, fontsize=11)
            plt.xlabel('degree  ')
            plt.ylabel('% genes ')
            # plt.title('Degree Distribution of ' + str(title) + ' vs Simulation')

            plt.tight_layout()
            plt.savefig(str(title) + ".png", dpi=300,bbox='tight')  # http://matplotlib.org/api/figure_api.html#matplotlib.figure.Figure.savefig
            plt.clf()
            plt.cla()
            plt.close()

            i += 1


def plot_em(real_net_file, sim_net_file, plot_title):
    #update_rcParams()
    # each line in 'input.txt' should be: [network name (spaces allowed) followed by /path/to/edge/file.txt/or/pickled/network.dump]
    input_files = open(real_net_file,'r').readlines()

    colors = ['#ADECD7', '#ADC0F3','#E4B2FB','#FBB2B2','#FFCC66','#C3F708']
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
        ENR = 0
        for j in range(repeats):
            sample_nodes = rd.sample(M.nodes(), num_nodes)
            ENR += len(M.edges(sample_nodes))/float(len(sample_nodes))
            #if (j==0): print(title + " has ENR = " + str(len(M.edges())/float(len(M.nodes()))) + ".\n")
            #with open (network_file,''
            #print (network_file.split('/')[-1].strip()+"\tnodes "+str(len(M.nodes()))+"\tedges "+str(len(M.edges())))

            degrees = list(M.degree(sample_nodes).values())
            in_degrees, out_degrees = list(M.in_degree(sample_nodes).values()), list(M.out_degree(sample_nodes).values())
            #degrees = in_degrees + out_degrees

            #NP GET FREQS
            degs, freqs = np.unique(degrees, return_counts=True)
            tot = float(sum(freqs))
            freqs = [(f/tot)*100 for f in freqs]

            plt.loglog(degs, freqs, basex=10, basey=10, linestyle='',  linewidth=2, color = colors[i], alpha=0.25, markersize=8, marker='.', markeredgecolor='None', )
            # you can also scatter the in/out degrees on the same plot
            # plt.scatter( .... )


        #i think one patch per set of samples?
        patch =  mpatches.Patch(color=colors[i], label=title)
        ENR /= repeats
        #print("Avg ENR " + str(title) + " = " + str(ENR) )

        H = H + [patch]

        #PLOT SIM NET
        degrees = list(sim_net.degree().values())
        in_degrees, out_degrees = list(sim_net.in_degree().values()), list(sim_net.out_degree().values())
        # degrees = in_degrees + out_degrees
        degs, freqs = np.unique(degrees, return_counts=True)
        tot = float(sum(freqs))
        freqs = [(f / tot) * 100 for f in freqs]

        plt.loglog(degs, freqs, basex=10, basey=10, linestyle='', linewidth=.5, color='#000000', alpha=1, markersize=10, marker='.', markeredgecolor='None')

        patch = mpatches.Patch(color='#000000', label="Simulation")

        H = H + [patch]

        #FORMAT PLOT
        ax = plt.gca() # gca = get current axes instance

        # if you are plotting a single network, you can add a text describing the fitness function used:
        #ax.text(.5,.7,r'$f(N)=\prod\frac {b}{b+d}\times\sum_{j=1}^{n} etc$', horizontalalignment='center', transform=ax.transAxes, size=20)
        # change (x,y)=(.5, .7) to position the text in a good location; the "f(N)=\sum \frac{}" is a mathematical expression using latex, see this:
        # https://www.sharelatex.com/learn/Mathematical_expressions
        # http://matplotlib.org/users/usetex.html

        #ax.set_xscale('log')
        #ax.set_yscale('log')
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
        #plt.title('Degree Distribution of ' + str(title) + ' vs Simulation')

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
##################################################################
def update_rcParams():
    font_path = '/home/2014/choppe1/Documents/EvoNet/virt_workspace/fonts/adobe/Adobe_Caslon_Pro_Regular.ttf'
    prop = font_manager.FontProperties(fname=font_path)
    rcParams['font.family'] = prop.get_name()
    rcParams['font.serif']         = 'Helvetica' #['Bitstream Vera Sans', 'DejaVu Sans', 'Lucida Grande', 'Verdana', 'Geneva', 'Lucid', 'Arial', 'Helvetica', 'Avant Garde', 'sans-serif']

    rcParams['axes.labelsize'] = 16
    rcParams['axes.titlesize'] = 20
    rcParams['grid.alpha'] = 0.1
    rcParams['axes.grid']=False
    rcParams['savefig.pad_inches']=.001
    rcParams['grid.color']='grey'

    rcParams['xtick.color']        =  'black'    #  ax.tick_params(axis='x', colors='red'). This will set both the tick and ticklabel to this color. To change labels' color, use: for t in ax.xaxis.get_ticklabels(): t.set_color('red')
    rcParams['xtick.direction']    =  'out'      # ax.get_yaxis().set_tick_params(which='both', direction='out')
    rcParams['xtick.labelsize']    =  12
    rcParams['xtick.major.pad']    =  1.0
    rcParams['xtick.major.size']   =  6     # how long the tick is
    rcParams['xtick.major.width']  =  1
    rcParams['xtick.minor.pad']    =  1.0
    rcParams['xtick.minor.size']   =  2.5
    rcParams['xtick.minor.width']  =  0.5
    rcParams['xtick.minor.visible']=  False


    rcParams['ytick.color']        =  'black'       # ax.tick_params(axis='x', colors='red')
    rcParams['ytick.direction']    =  'out'         # ax.get_xaxis().set_tick_params(which='both', direction='out')
    rcParams['ytick.labelsize']    =  12
    rcParams['ytick.major.pad']    =  2
    rcParams['ytick.major.size']   =  6
    rcParams['ytick.major.width']  =  1
    rcParams['ytick.minor.pad']    =  2.0
    rcParams['ytick.minor.size']   =  2.5
    rcParams['ytick.minor.width']  =  0.5
    rcParams['ytick.minor.visible']=  False
    return prop
##################################################################


if __name__ == "__main__":
    base_dir = "/home/2014/choppe1/Documents/EvoNet/virt_workspace/data/output/conf2/" #customize for curr work
    real_net_file = "/home/2014/choppe1/Documents/EvoNet/virt_workspace/data/input/input_all_nets.txt" #check this is still on yamaska

    pairs = sys.argv[1:]
    print("plotting " + str(len(pairs)) + " dirs for comparison.\n")

    for pair in pairs:
        sim, real_name = pair.split('/')
        print("Plotting sim dir " + str(sim) + " vs real " + str(real_name) + "\n")
        sim_dirr = str(base_dir + sim)

        if not os.path.exists(sim_dirr + "/comparison_plots/"):
            os.makedirs(sim_dirr + "/comparison_plots/")
        for sim_file in os.listdir(sim_dirr+"/nets/"):
            print("Plotting sim file " + str(sim_file))
            plot_pairs(real_net_file, real_name, sim_dirr +"/nets/"+ sim_file, sim_dirr + "/comparison_plots/" + sim_file)

    print("\nDone.\n")
