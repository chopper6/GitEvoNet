#!/usr/bin/python3
import matplotlib, os, csv, sys, math
matplotlib.use('Agg') # This must be done before importing matplotlib.pyplot
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


#ORGANIZER
def single_run_plots (dirr):
    #plots features_over_time and degree_distrib
    #only uses most fit indiv in population
    if not os.path.exists(dirr):
        print("ERROR plot_nets(): given directory not found: " + str(dirr))
        return

    net_info, titles = parse_info(dirr)

    if not os.path.exists(dirr + "/images_by_size/"):
        os.makedirs(dirr + "/images_by_size/")
    if not os.path.exists(dirr + "/images_by_time/"):
        os.makedirs(dirr + "/images_by_time/")


    mins, maxs = 0,0
    features_over_size(dirr, net_info, titles, mins, maxs, False)
    features_over_time(dirr, net_info, titles, mins, maxs, False)

    #solver_time(dirr)

    print("Generating degree distribution plots.")
    degree_distrib(dirr)
    degree_distrib_change(dirr)



#IMAGE GENERATION FNS()
def degree_distrib(dirr):
        deg_file_name = dirr + "/degree_distrib.csv"

        if not os.path.exists(dirr + "/degree_distribution/"):
            os.makedirs(dirr + "/degree_distribution/")

        all_lines = [Line.strip() for Line in (open(deg_file_name,'r')).readlines()]
        titles = all_lines[0]
        img_index = 0
        for line in all_lines[1:]:
            line = line.replace('[', '').replace(']','').replace("\n", '')
            line = line.split(',')
            gen = line[0]
            in_deg = line[2].split(" ")
            in_deg_freq = line[3].split(" ")
            out_deg = line[4].split(" ")
            out_deg_freq = line[5].split(" ")

            in_deg = list(filter(None, in_deg))
            in_deg_freq = list(filter(None, in_deg_freq))
            out_deg = list(filter(None, out_deg))
            out_deg_freq = list(filter(None, out_deg_freq))


            # plot in degrees
            plt.loglog(in_deg, in_deg_freq, basex=10, basey=10, linestyle='', color='blue', alpha=0.7, markersize=7, marker='o', markeredgecolor='blue')

            #plot out degrees on same figure
            plt.loglog(out_deg, out_deg_freq, basex=10, basey=10, linestyle='', color='green', alpha=0.7, markersize=7, marker='D', markeredgecolor='green')

            #way to not do every time?
            ax = matplotlib.pyplot.gca()
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

            plt.tick_params(  # http://matplotlib.org/api/axes_api.html#matplotlib.axes.Axes.tick_params
                axis='both',  # changes apply to the x-axis
                which='both',  # both major and minor ticks are affected
                right='off',  # ticks along the right edge are off
                top='off',  # ticks along the top edge are off
            )
            in_patch = mpatches.Patch(color='blue', label='In-degree')
            out_patch = mpatches.Patch(color='green', label='Out-degree')
            plt.legend(loc='upper right', handles=[in_patch, out_patch], frameon=False)
            plt.xlabel('Degree (log) ')
            plt.ylabel('Number of nodes with that degree (log)')
            plt.title('Degree Distribution of Fittest Net at Generation ' + str(gen))
            plt.xlim(1,1000)
            plt.ylim(1,1000)
            plt.savefig(dirr + "/degree_distribution/" + str(gen) + ".png", dpi=300)
            plt.clf()
            img_index += 1


def features_over_size(dirr, net_info, titles, mins, maxs, use_lims):
    #size is 2nd col of net info

    img_dirr = dirr + "/images_by_size/"
    for i in range(len(titles)):
        num_outputs = len(net_info)
        ydata = []
        xdata = []
        for j in range(num_outputs):
            ydata.append(net_info[j,i])
            xdata.append(net_info[j,1])
        x_ticks = []
        max_net_size = max(xdata)
        for j in range(0,11):
            x_ticks.append((max_net_size/10)*j)
        plt.plot(xdata, ydata)
        plt.ylabel(titles[i] + " of most fit Individual")
        plt.title(titles[i])
        if (use_lims==True): plt.ylim(mins[i], maxs[i])
        plt.xlabel("Net Size")
        plt.xticks(x_ticks, x_ticks)
        plt.savefig(img_dirr + str(titles[i]) + ".png")
        plt.clf()
    return

def growth_deg_change(dirr):
    deg_file_name = dirr + "/growth_degree_change.csv"

    if not os.path.exists(dirr + "/degree_distribution_change/"):
        os.makedirs(dirr + "/degree_distribution_change/")

    all_lines = [Line.strip() for Line in (open(deg_file_name, 'r')).readlines()]

    patches = []
    colors = ['#99ffcc', '#00ffcc', '#009999', '#000000'] #ADD EM
    gens = ['500','1000','2000','4000']
    i=0
    for line in all_lines:
        line = line.replace('[', '').replace(']', '').replace("\n", '')
        line = line.split(',')
        deg = line[0].split(" ")
        deg_freq = line[1].split(" ")

        degs = list(filter(None, deg))
        freqs = list(filter(None, deg_freq))

        patch = mpatches.Patch(color=colors[i], label=gens[i])
        patches.append(patch)
        plt.loglog(degs, freqs, basex=10, basey=10, linestyle='', color=colors[i], alpha=0.8, markersize=7, marker='o', markeredgecolor=colors[i])
        #plt.scatter(degs, freqs, c=colors[i], alpha=0.8, s=40, marker='o')
        i+=1


    ax = matplotlib.pyplot.gca()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    #ax.set_xlim([1,16])
    #ax.set_ylim([1,200])
    #ax.set_yticks([0,50,100,150,200])
    #ax.set_xticks([0,2,4,6,8,10,12,14,16])

    plt.tick_params(  # http://matplotlib.org/api/axes_api.html#matplotlib.axes.Axes.tick_params
        axis='both',  # changes apply to the x-axis
        which='both',  # both major and minor ticks are affected
        right='off',  # ticks along the right edge are off
        top='off',  # ticks along the top edge are off
    )
    
    plt.legend(loc='upper right', handles=patches, frameon=False)
    plt.xlabel('Degree')
    plt.ylabel('Number of Nodes with Given Degree')
    plt.title('Change in Degree Distribution')
    plt.savefig(dirr + "/degree_distribution_change/in_degree_change.png")
    plt.clf()

def degree_distrib_change(dirr):
    deg_file_name = dirr + "/degree_change.csv"

    if not os.path.exists(dirr + "/degree_distribution_change/"):
        os.makedirs(dirr + "/degree_distribution_change/")

    all_lines = [Line.strip() for Line in (open(deg_file_name, 'r')).readlines()]
    if (len(all_lines) != 3): 
        print ("WARNING: Degree_distrib_diff(): should only have 3 lines in csv, instead found " + str(len(all_lines)) + ", returning without plotting degree change.")
        return
    titles = all_lines[0]

    # Get starting degree distribution
    line = all_lines[1]
    line = line.replace('[', '').replace(']', '').replace("\n", '')
    line = line.split(',')
    deg = line[0].split(" ")
    deg_freq = line[1].split(" ")

    start_deg = list(filter(None, deg))
    start_freq = list(filter(None, deg_freq))

    # Get ending degree distribution
    line = all_lines[2]
    line = line.replace('[', '').replace(']', '').replace("\n", '')
    line = line.split(',')
    deg = line[0].split(" ")
    deg_freq = line[1].split(" ")

    end_deg = list(filter(None, deg))
    end_freq = list(filter(None, deg_freq))
    '''
    # Manually combine degrees
    start_deg = []
    start_freq = []
    end_deg, end_freq = [], []
    for in_i in len(start_in_deg):
        deg = start_in_deg[in_i]
        if deg in start_out_deg:
            out_i = start_out_deg.index(deg)
            freq = start_in_deg_freq[in_i] + start_out_deg_freq[out_i]
            start_out_deg.remove(deg)
            start_out_freq.remove(start_out_freq[out_i])
        else: freq = start_in_deg_freq[in_i]

        start_deg.append(deg)
        start_freq.append(freq)
    for out_i in len(start_out_deg):  #rm'd all that are in in_deg     
        start_deg.append(start_out_deg[out_i])
        start_freq.append(start_out_freq[out_i])

 

    for in_i in len(end_in_deg):
        deg = end_in_deg[in_i]
        if deg in end_out_deg:
            out_i = end_out_deg.index(deg)
            freq = end_in_deg_freq[in_i] + end_out_deg_freq[out_i]
            end_out_deg.remove(deg)
            end_out_freq.remove(end_out_freq[out_i])
        else: freq = end_in_deg_freq[in_i]

        end_deg.append(deg)
        end_freq.append(freq)

    for out_i in len(end_out_deg):  #rm'd all that are in in_deg
        end_deg.append(end_out_deg[out_i])
        end_freq.append(end_out_freq[out_i])

    '''
    start_col = '#ff5050'
    end_col = '#0099cc'
    # CHANGE IN DEGREE
    # plot start in degrees
    plt.scatter(start_deg, start_freq, c=start_col, alpha=0.8, s=40, marker='o')

    # plot end in degrees on same figure
    plt.scatter(end_deg, end_freq, c=end_col, alpha=0.8, s=40, marker='o')

    ax = matplotlib.pyplot.gca()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xlim([1,16])
    ax.set_ylim([1,200])
    ax.set_yticks([0,50,100,150,200])
    ax.set_xticks([0,2,4,6,8,10,12,14,16])

    plt.tick_params(  # http://matplotlib.org/api/axes_api.html#matplotlib.axes.Axes.tick_params
        axis='both',  # changes apply to the x-axis
        which='both',  # both major and minor ticks are affected
        right='off',  # ticks along the right edge are off
        top='off',  # ticks along the top edge are off
    )
    in_patch = mpatches.Patch(color=start_col, label='Initial Degree Frequency')
    out_patch = mpatches.Patch(color=end_col, label='Final Degree Frequency')
    plt.legend(loc='upper right', handles=[in_patch, out_patch], frameon=False)
    plt.xlabel('Degree')
    plt.ylabel('Number of Nodes with Given Degree')
    plt.title('Change in Degree Distribution')
    plt.savefig(dirr + "/degree_distribution_change/in_degree_change.png", dpi=300)
    plt.clf()

    '''
    # CHANGE IN OUT DEGREES
    plt.loglog(start_out_deg, start_out_deg_freq, basex=10, basey=10, linestyle='', color='purple', alpha=0.7, markersize=7, marker='D', markeredgecolor='purple')
    plt.loglog(end_out_deg, end_out_deg_freq, basex=10, basey=10, linestyle='', color='green', alpha=0.7, markersize=7, marker='D', markeredgecolor='green')

    ax = matplotlib.pyplot.gca()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tick_params(  # http://matplotlib.org/api/axes_api.html#matplotlib.axes.Axes.tick_params
        axis='both',  # changes apply to the x-axis
        which='both',  # both major and minor ticks are affected
        right='off',  # ticks along the right edge are off
        top='off',  # ticks along the top edge are off
    )
    in_patch = mpatches.Patch(color='purple', label='Out-degree at Start')
    out_patch = mpatches.Patch(color='green', label='Out-degree at End')
    plt.legend(loc='upper right', handles=[in_patch, out_patch], frameon=False)
    plt.xlabel('Degree (log) ')
    plt.ylabel('Number of nodes with that degree (log)')
    plt.title('Change in Out Degree Distribution of Fittest Net')
    plt.xlim(1, 1000)
    plt.ylim(1, 1000)
    plt.savefig(dirr + "/degree_distribution_change/out_degree_change.png", dpi=300)
    plt.clf()
    '''


def features_over_time(dirr, net_info, titles, mins, maxs, use_lims):
    img_dirr = dirr + "/images_by_time/"
    for i in range(len(titles)):
        num_outputs = len(net_info)
        ydata = []
        xdata = []
        for j in range(num_outputs):
            ydata.append(net_info[j, i])
            xdata.append(net_info[j, 0])

        if (titles[i] == ' Fitness'):
            ydata2 = []
            for y in ydata:
                ydata2.append(math.log(y,10))
            ydata = ydata2   
            titles[i] += ' Log-Scaled'
        x_ticks = []
        max_gen = xdata[-1]
        for j in range(0, 11):
            x_ticks.append(int((max_gen / 10) * j))
        plt.plot(xdata, ydata)

        #TEMP for conf 
        '''
        ax = plt.gca() 

        if(titles[i] == ' Leaf Measure'):
            plt.ylabel("Leaf Fitness")
            ax.set_ylim([0,.3])
            ax.set_xlim([0,2000])
            plt.title("Network Leaf Fitness")
            ticks = [0, .1, .2, .3, .4]
            ax.set_yticks(ticks)
            ticks = [0, 400, 800, 1200, 1600, 2000]
            ax.set_xticks(ticks)
        elif(titles[i] == '  Hub Measure'):
            plt.ylabel("Hub Fitness")
            ax.set_ylim([0,.1])
            ax.set_xlim([0,2000])
            plt.title("Network Hub Fitness")
            ticks = [0, .02, .04, .06, .08]
            ax.set_yticks(ticks)
            ticks = [0, 400, 800, 1200, 1600, 2000]
            ax.set_xticks(ticks)
        elif(titles[i] == ' Fitness'):
            plt.ylabel("Fitness")
            ax.set_ylim([0,.025])
            ax.set_xlim([0,2000])
            plt.title("Network Fitness")
            ticks = [0, .005, .01, .015, .02, .025]
            ax.set_yticks(ticks)
            ticks = [0, 400, 800, 1200, 1600, 2000]
            ax.set_xticks(ticks)
                
        else: 
            plt.ylabel(titles[i])
            plt.title(titles[i])
        '''
        plt.ylabel(titles[i])
        plt.title(titles[i])
        if (use_lims == True): plt.ylim(mins[i], maxs[i])
        plt.xlabel("Generation")
        plt.xticks(x_ticks, x_ticks)
        plt.savefig(img_dirr + str(titles[i]) + ".png")
        plt.clf()
    return

def solver_time(dirr):
    img_dirr = dirr + "/images_by_size/"
    with open(dirr + "/timing.csv", 'r') as timing_csv:
        lines = timing_csv.readlines()
        title = lines[0]
        net_size=[]
        time=[]
        for line in lines[1:]:
            line = line.split(",")
            line[-1].replace("\n",'')
            net_size.append(line[0])
            time.append(line[1])
        max_net_line = lines[-1].split(",")
        max_net_size = int(max_net_line[0])
    x_ticks = []
    for j in range(0, 11):
        x_ticks.append(int((max_net_size / 10) * j))
    plt.plot(net_size,time)
    plt.xlabel("Net Size")
    plt.ylabel("Seconds to Pressurize")
    plt.title("Pressurize Time as Networks Grow")
    plt.xticks(x_ticks, x_ticks)
    plt.savefig(img_dirr + "pressurize_time")
    plt.clf()

#HELPER FNS()
def parse_info(dirr):
    #returns 2d array of outputs by features
    #note that feature[0] is the net size

    with open(dirr + "/info.csv", 'r') as info_csv:
        lines = info_csv.readlines()
        titles = lines[0].split(",")
        piece = titles[-1].split("\n")
        titles[-1] = piece[0]
        num_features = len(titles)
        num_output = len(lines)-1
        master_info = np.empty((num_output, num_features))

        for i in range(0,num_output):
            row = lines[i+1].split(",", num_features) 
            piece = row[-1].split("\n")
            row[-1] = piece[0]
            master_info[i] = row

    return master_info, titles 


if __name__ == "__main__":
    #first bash arg should be parent directory, then each child directory
    dirr_base = "/home/2014/choppe1/Documents/EvoNet/virt_workspace/data/output/"
    dirr_parent = sys.argv[1]
    dirr_base += dirr_parent

    for arg in sys.argv[2:]:
        print("Plotting dirr " + str(arg))
        dirr_addon = arg
        dirr= dirr_base + dirr_addon
        single_run_plots(dirr)
        growth_deg_change(dirr)
