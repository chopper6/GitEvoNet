#!/usr/bin/python3
import math, matplotlib, os, csv
matplotlib.use('Agg') # This must be done before importing matplotlib.pyplot
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


#ORGANIZER
def param_plots (dirr, num_workers, gens, output_freq, num_indivs, use_lims):
    #writes outro csv
    #plots features_over_time, features_over_params, degree_distrib
    worker_info, titles = parse_worker_info(dirr, num_workers, gens, num_indivs, output_freq)

    mins, maxs, endpts = write_outro (dirr, num_workers, gens, num_indivs, output_freq, worker_info, titles)

    init_img(dirr, num_workers)

    fitness_over_params(dirr, num_workers, endpts, titles)

    features_over_time(dirr, num_workers, gens, num_indivs, output_freq, worker_info, titles, mins, maxs, use_lims)

    print("Generating degree distribution plots.")
    degree_distrib(dirr, num_workers, gens, output_freq)

def single_run_plots (dirr, gens, output_freq, num_indivs):
    #writes outro csv
    #plots features_over_time, features_over_params, degree_distrib

    if not os.path.exists(dirr + "/images/"):
        os.makedirs(dirr + "/images/")

    master_info, titles = parse_info(dirr, gens, num_indivs, output_freq)

    mins, maxs = 0,0

    features_over_time(dirr, gens, num_indivs, output_freq, master_info, titles, mins, maxs, False)

    print("Generating degree distribution plots.")
    degree_distrib(dirr, gens, output_freq)



def write_outro (dirr, num_workers, gens, num_indivs, output_freq, worker_info, titles):

    num_features = len(titles)
    mins = [100000 for i in range(num_features)]
    maxs = [0 for i in range(num_features)]
    endpts = [[0 for i in range(num_features)] for j in range(num_workers)]

    with open(dirr + "/outro_info.csv", 'w') as outro_file:
        output = csv.writer(outro_file)

        header = ["Param Set #"]
        for i in range(num_features):
            header += ["Min" + str(titles[i])]
            header += ["Max" + str(titles[i])]
            header += ["Endpoint" + str(titles[i])]

        output.writerow(header)

        for w in range(num_workers):
            row = []
            row.append(w)
            for i in range(0,num_features):
                vals = []
                feature_endpts = []
                for j in range(num_indivs):
                    for g in range(int(gens*output_freq)):
                        vals.append(worker_info[w,g,j,i]) #titles are one off since net size not included
                    feature_endpts.append(worker_info[w,int(gens*output_freq)-1,j,i])
                minn = min(vals)
                maxx = max(vals)
                endpt = max(feature_endpts)
                endpts[w][i] = endpt
                row.append(minn)
                row.append(maxx)
                row.append(endpt)
                mins[i] = min(minn, mins[i])
                maxs[i] = max(maxx, maxs[i])
            output.writerow(row)

    return mins, maxs, endpts


#IMAGE GENERATION FNS()
def degree_distrib(dirr, gens, output_freq):
        deg_file_name = dirr + "degree_distrib.csv"

        if not os.path.exists(dirr + "/degree_distribution/"):
            os.makedirs(dirr + "/degree_distribution/")

        with open(deg_file_name,'r') as deg_file:
            titles = deg_file.readline().split(",")
            piece = titles[-1].split("\n")
            titles[-1] = piece[0]
            for i in range(int(gens * output_freq)):
                line = str(deg_file.readline())
                line = line.split(',')
                print(line[0],line[1])
                line = line.replace('[', '').replace(']','').replace("\n", '')

                in_deg = line[1].split(" ")
                in_deg_freq = line[2].split(" ")
                out_deg = line[3].split(" ")
                out_deg_freq = line[4].split(" ")

                in_deg = list(filter(None, in_deg))
                in_deg_freq = list(filter(None, in_deg_freq))
                out_deg = list(filter(None, out_deg))
                out_deg_freq = list(filter(None, out_deg_freq))

                # plot in degrees
                #print(in_deg, in_deg_freq)
                print(in_deg, in_deg_freq, out_deg, out_deg_freq)
                plt.loglog(in_deg, in_deg_freq, basex=10, basey=10, linestyle='', color='blue', alpha=0.7, markersize=7, marker='o', markeredgecolor='blue')

                #plot out degrees on same figure
                #print(out_deg, out_deg_freq)
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
                plt.xlim(1,1000)
                plt.ylim(1,1000)
                plt.savefig(dirr + "/degree_distribution/" + str(i) + ".png", dpi=300)
                plt.clf()


def features_over_time(dirr, gens, num_indivs, output_freq, worker_info, titles, mins, maxs, use_lims):

        img_dirr = dirr + "/images/"
        for i in range(len(titles)):
            x_ticks = []
            buffer_ticks = []
            for j in range(num_indivs):
                data = []
                for g in range(int(gens*output_freq)):
                    data.append(worker_info[g,j,i]) #titles are one off since net size not included
                    if (j==0 and g%10 == 0): 
                        x_ticks.append(int(g/output_freq))
                        buffer_ticks.append(g)
                #print(data)
                plt.plot(data)
            plt.ylabel(titles[i] + " of each Individual")
            plt.title(titles[i])
            if (use_lims==True): plt.ylim(mins[i], maxs[i])
            plt.xlabel("Generation")
            plt.xticks(buffer_ticks, x_ticks)
            plt.savefig(img_dirr + str(titles[i]))
            plt.clf()


        return


def fitness_over_params(dirr, num_workers, feature_info, titles):

    num_features = len(titles)
    for i in range (num_features):
        x = []
        y = []
        xticks = []
        for w in range(num_workers):
            x.append(w)
            y.append(feature_info[w][i])
            xticks.append(w)
        plt.bar(x,y, align="center")
        plt.xticks(xticks)
        plt.title(titles[i])
        plt.xlabel("Parameter Set")
        plt.ylabel("Feature Value at Final Generation")
        plt.savefig(dirr + "/param_images/" + str(titles[i]) + ".png")
        plt.clf()



#HELPER FNS()
def parse_info(dirr, gens, num_indivs, output_freq):
    #returns 4D array with [worker#][gen][indiv#][feature]

    master_info = None
    titles = None
    num_features = 0 #assumes same num features in worker and master

    with open(dirr + "/info.csv", 'r') as info_csv:
        titles = info_csv.readline().split(",")
        piece = titles[-1].split("\n")
        titles[-1] = piece[0]
        num_features = len(titles)-1
        master_info = np.empty((int(gens*output_freq), num_indivs, num_features))

        for i in range(num_indivs * int(gens*output_freq)):
            row = info_csv.readline().split(",", num_features) #might be num_features -1 now
            piece = row[-1].split("\n")
            row[-1] = piece[0]
            print(row[1:])
            master_info[math.floor(i / num_indivs)][0] = row[1:]  # not sure why need to index whole array


    return master_info, titles[1:] #trims net# from titles since already included in worker_info ordering




def parse_worker_info(dirr, num_workers, gens, num_indivs, output_freq):
    #returns 4D array with [worker#][gen][indiv#][feature]

    worker_info = None
    titles = None
    num_features = 0 #assumes same num features in worker and master
    #master_info = list(csv.reader(open(dirr+"/master/info.csv"),'r'))

    for w in range(num_workers):

        with open(dirr + "/" + str(w) + "/info.csv", 'r') as info_csv:
            if (w==0):
                titles = info_csv.readline().split(",")
                piece = titles[-1].split("\n")
                titles[-1] = piece[0]
                num_features = len(titles)-1
                worker_info = np.empty((num_workers, int(gens*output_freq), num_indivs, num_features))
            else:
                next(info_csv)

            for i in range(num_indivs * int(gens*output_freq)):
                row = info_csv.readline().split(",", num_features) #might be num_features -1 now
                piece = row[-1].split("\n")
                row[-1] = piece[0]
                worker_info[w][math.floor(i / num_indivs)][int(row[0])] = row[1:]  # not sure why need to index whole array
            #print(worker_info[1][:][0])


    return worker_info, titles[1:] #trims net# from titles since already included in worker_info ordering


if __name__ == "__main__":
    dirr = "/home/2014/choppe1/Documents/EvoNet/virt_workspace/data/output/parv2_5/"

    single_run_plots(dirr, 800, .05, 1)
    #single_run_plots(dirr, gens, output_freq, num_indivs):
