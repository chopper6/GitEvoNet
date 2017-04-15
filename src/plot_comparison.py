import matplotlib
matplotlib.use('Agg') # you need this line if you're running this code on rupert
import sys, os, matplotlib.pyplot as plt, matplotlib.patches as mpatches, networkx as nx, numpy as np
#from scipy.stats import itemfreq
from ticker import FuncFormatter

def plot_em(input_net_file):
    # each line in 'input.txt' should be: [network name (spaces allowed) followed by /path/to/edge/file.txt/or/pickled/network.dump]
    input_files = open(input_net_file,'w').readlines()

    colors      = ['b', 'c', 'g','r','y','m','purple','grey'], # pick more colors from here: http://htmlcolorcodes.com/ , number of colos >= number of networks in input_files ]
    i = 0
    for  line in input_files:
        line         = line.strip()
        title        = line.split()[:-1][0]
        network_file = line.split()[-1]

        # if networks are edge files, load them using load_network(), if they're pickled (faster) load them using nx's read_gpickle
        #M = init.load_network ({'network_file':network_file.strip(), 'biased':False})
        #M = nx.read_edgelist(network_file.strip(),nodetype=int,create_using=nx.DiGraph())
        #nx.write_gpickle(M,'dumps/'+network_file.split('/')[-1].split('.')[0]+'.dump')
        M = nx.read_gpickle(network_file)


        #with open (network_file,''
        print (network_file.split('/')[-1].strip()+"\tnodes "+str(len(M.nodes()))+"\tedges "+str(len(M.edges())))

        degrees = list(M.degree().values())
        #SCIPY GET FREQS
        #tmp     = itemfreq(degrees) # Get the item frequencies
        #degs, freqs =  tmp[:, 0], tmp[:, 1] # 0 = unique values in data, 1 = frequencies

        #NP GET FREQS
        degs, freqs = np.unique(degrees, return_counts=True)
        degs = np.array2string(degs).replace('\n', '')
        freqs = np.array2string(freqs).replace('\n', '')

        # changing freqs into %
        tot = float(sum(freqs))
        freqs = [(f/tot)*100 for f in freqs]

        plt.loglog(degs, freqs, basex=10, basey=10, linestyle='-',  linewidth=2, color = colors[i], alpha=0.5, markersize=8, marker='', markeredgecolor='None')
        # you can also scatter the in/out degrees on the same plot
        # plt.scatter( .... )

        patch =  mpatches.Patch(color=colors[i], label=title)

        H = H + [patch]
        i+=1

    ax = plt.gca() # gca = get current axes instance

    # if you are plotting a single network, you can add a text describing the fitness function used:
    ax.text(.5,.7,r'$f(N)=\prod\frac {b}{b+d}\times\sum_{j=1}^{n} etc$', horizontalalignment='center', transform=ax.transAxes, size=20)
    # change (x,y)=(.5, .7) to position the text in a good location; the "f(N)=\sum \frac{}" is a mathematical expression using latex, see this:
    # https://www.sharelatex.com/learn/Mathematical_expressions
    # http://matplotlib.org/users/usetex.html

    ax.set_xlim([0.7,1000])
    ax.set_ylim([.02,100])
    ax.get_xaxis().set_major_formatter(ticker.FuncFormatter(LogXformatter))
    ax.get_yaxis().set_major_formatter(ticker.FuncFormatter(LogYformatter))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tick_params(axis='both', which='both', right='off', top='off') #http://matplotlib.org/api/axes_api.html#matplotlib.axes.Axes.tick_params
    plt.legend(loc='upper right', handles=H, frameon=False,fontsize= 11)
    plt.xlabel('degree  ')
    plt.ylabel('% genes ')
    plt.title('Degree Distribution')

    plt.tight_layout()
    plt.savefig("deg-dist.png", dpi=300,bbox='tight') # http://matplotlib.org/api/figure_api.html#matplotlib.figure.Figure.savefig

    print ("\n\nplotted: deg-dist.png")


if __name__ == "__main__":
    print('starting...')
    input_net_file = sys.argv[1]
    plot_em(input_net_file)
