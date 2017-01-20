#!/usr/bin/python3
import matplotlib, os, csv
matplotlib.use('Agg') # This must be done before importing matplotlib.pyplot
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


#ORGANIZER
def single_run_plots (dirr):
    #plots features_over_time and degree_distrib
    #only uses most fit indiv in population

    if not os.path.exists(dirr + "/images_by_size/"):
        os.makedirs(dirr + "/images_by_size/")
    if not os.path.exists(dirr + "/images_by_time/"):
        os.makedirs(dirr + "/images_by_time/")

    net_info, titles = parse_info(dirr)

    mins, maxs = 0,0
    features_over_size(dirr, net_info, titles, mins, maxs, False)
    features_over_time(dirr, net_info, titles, mins, maxs, False)

    solver_time(dirr)

    print("Generating degree distribution plots.")
    degree_distrib(dirr)



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
            in_deg = line[1].split(" ")
            in_deg_freq = line[2].split(" ")
            out_deg = line[3].split(" ")
            out_deg_freq = line[4].split(" ")

            in_deg = list(filter(None, in_deg))
            in_deg_freq = list(filter(None, in_deg_freq))
            out_deg = list(filter(None, out_deg))
            out_deg_freq = list(filter(None, out_deg_freq))

            for ele in out_deg_freq:
                if (ele == '"'):
                    out_deg_freq.remove(ele)
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
            plt.title('Degree Distribution (network size = ' + str(line[0]) + ' nodes) of Most Fit Net')
            plt.xlim(1,100)
            plt.ylim(1,1000)
            plt.savefig(dirr + "/degree_distribution/" + str(img_index) + ".png", dpi=300)
            plt.clf()
            img_index += 1


def features_over_size(dirr, net_info, titles, mins, maxs, use_lims):

        img_dirr = dirr + "/images_by_size/"
        for i in range(len(titles)):
            num_outputs = len(net_info)
            ydata = []
            xdata = []
            for j in range(num_outputs):
                ydata.append(net_info[j,i])
                xdata.append(net_info[j,0])
                #change x_ticks?
                #x_ticks.append(int(g/output_freq))
                #buffer_ticks.append(gi)
            x_ticks = []
            max_net_size = net_info[num_outputs-1,0]
            for j in range(0,11):
                x_ticks.append((max_net_size/10)*j)
            plt.plot(xdata, ydata)
            plt.ylabel(titles[i] + " of most fit Individual")
            plt.title(titles[i])
            if (use_lims==True): plt.ylim(mins[i], maxs[i])
            plt.xlabel("Net Size")
            plt.xticks(x_ticks, x_ticks)
            plt.savefig(img_dirr + str(titles[i]))
            plt.clf()


        return


def features_over_time(dirr, net_info, titles, mins, maxs, use_lims):
    img_dirr = dirr + "/images_by_time/"
    for i in range(len(titles)):
        num_outputs = len(net_info)
        ydata = []
        xdata = []
        for j in range(num_outputs):
            ydata.append(net_info[j, i])
            xdata.append(j)
            # change x_ticks?
            # x_ticks.append(int(g/output_freq))
            # buffer_ticks.append(gi)
        x_ticks = []
        max_net_size = net_info[num_outputs - 1, 0]
        for j in range(0, 11):
            x_ticks.append((num_outputs / 10) * j)
        plt.plot(xdata, ydata)
        plt.ylabel(titles[i] + " of most fit Individual")
        plt.title(titles[i])
        if (use_lims == True): plt.ylim(mins[i], maxs[i])
        plt.xlabel("Master Generation")
        plt.xticks(x_ticks, x_ticks)
        plt.savefig(img_dirr + str(titles[i]))
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
        x_ticks.append((max_net_size / 10) * j)
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
    dirr = "/home/2014/choppe1/Documents/EvoNet/virt_workspace/data/output/batch2_mutn/2"

    single_run_plots(dirr)
