#!/usr/bin/python3
import math, matplotlib, os, csv
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

matplotlib.use('Agg') # This must be done before importing matplotlib.pyplot
import numpy as np


#ORGANIZER
def param_plots (dirr, num_workers, gens, output_freq, num_indivs):
    #writes outro csv
    #plots features_over_time, features_over_params, degree_distrib
    worker_info, titles = parse_worker_info(dirr, num_workers, gens, num_indivs, output_freq)

    mins, maxs, endpts = write_outro (dirr, num_workers, gens, num_indivs, output_freq, worker_info, titles)

    init_img(dirr, num_workers)

    fitness_over_params(dirr, num_workers, endpts, titles)

    features_over_time(dirr, num_workers, gens, num_indivs, output_freq, worker_info, titles, mins, maxs)

    print("Generating degree distribution plots.")
    degree_distrib(dirr, num_workers, gens, output_freq)


def write_outro (dirr, num_workers, gens, num_indivs, output_freq, worker_info, titles):

    num_features = len(titles)
    mins = [100000 for i in range(num_features)]
    maxs = [0 for i in range(num_features)]
    endpts = [[0 for i in range(num_features)] for j in range(num_workers)]

    with open(dirr + "/outro_info.csv", 'w') as outro_file:
        output = csv.writer(outro_file)

        header = ["Worker #"]
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
def degree_distrib(dirr, num_workers, gens, output_freq):
    for w in range(num_workers):
        deg_file_name = dirr + "/" + str(w) + "/degree_distrib.csv"
        in_deg_distrib = [[None,None] for i in range(gens)]
        out_deg_distrib = [[None,None] for i in range(gens)]
        with open(deg_file_name,'r') as deg_file:
            titles = deg_file.readline().split(",")
            piece = titles[-1].split("\n")
            titles[-1] = piece[0]
            for i in range(int(gens * output_freq)):
                line = str(deg_file.readline())
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

                # plot in degrees
                #print(in_deg, in_deg_freq)
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
                plt.savefig(dirr + "/" + str(w) + "/degree_distribution/" + str(i) + ".png", dpi=300)
                plt.clf()


def features_over_time(dirr, num_workers,gens, num_indivs, output_freq, worker_info, titles, mins, maxs):

    #master plots
    '''
    m_dirr = dirr + "/images/master/"
    for i in range(1, len(titles) - 1):
        for j in range(num_indivs):
            data = []
            for g in range(gens):
                data.append(master_info[g, j, i])  # titles are one off since net size not included
            plt.plot(data)
        plt.savefig(m_dirr + str(titles[i]))
        plt.clf()
    '''

    #worker plots
    for w in range(num_workers):
        w_dirr = dirr +"/" + str(w) + "/images/"
        for i in range(len(titles)):
            x_ticks = []
            buffer_ticks = []
            for j in range(num_indivs):
                data = []
                for g in range(int(gens*output_freq)):
                    data.append(worker_info[w,g,j,i]) #titles are one off since net size not included
                    if (j==0 and g%10 == 0): 
                        x_ticks.append(int(g/output_freq))
                        buffer_ticks.append(g)
                #print(data)
                plt.plot(data)
            plt.ylabel(titles[i] + " of each Individual")
            plt.title(titles[i])
            plt.ylim(mins[i], maxs[i])
            plt.xlabel("Generation")
            plt.xticks(buffer_ticks, x_ticks)
            plt.savefig(w_dirr + str(titles[i]))
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
def init_img(dirr, num_workers):
    if not os.path.exists(dirr + "/master/images"):
        os.makedirs(dirr + "/master/images")
    if not os.path.exists(dirr + "/param_images"):
        os.makedirs(dirr + "/param_images")
    for w in range(num_workers):
        if not os.path.exists(dirr +"/" + str(w) + "/images/" ):
            os.makedirs(dirr +"/" + str(w) + "/images/")
        if not os.path.exists(dirr + "/" + str(w) + "/degree_distribution/"):
            os.makedirs(dirr +"/" + str(w) + "/degree_distribution/")


def merge_paramtest(dirr, num_workers):
    #curr naive output

    for w in range(num_workers):
        configs_file = dirr + "/" + str(w) + "/worker_configs.csv"
        outro_file = dirr + "/" + str(w) + "/outro_info.csv"

        with open(outro_file, 'r') as outro:
            if (w==0):
                titles = outro.readline().split(",")
                piece = titles[-1].split("\n")
                titles[-1] = piece[0]
                num_features = len(titles)
                feature_info = np.empty((num_workers, num_features))
            else: next(outro)
            features = outro.readline().split(",")
            piece = features[-1].split("\n")
            features[-1] = piece[0]
            #print("merge_paramtest() features: " + str(features))
            feature_info[w] = features
    return feature_info, titles



def parse_info(dirr, num_workers, gens, num_indivs):
    #returns 4D array with [worker#][gen][indiv#][feature]

    worker_info = None
    master_info = None
    titles = None
    num_features = 0 #assumes same num features in worker and master
    #master_info = list(csv.reader(open(dirr+"/master/info.csv"),'r'))

    with open(dirr+"/master/info.csv",'r') as info_csv:
        titles = info_csv.readline().split(",")
        num_features = len(titles)-1
        master_info = np.empty((gens, num_indivs, num_features))  # could print this info to 2nd line of file

        for i in range(num_indivs*gens):
            row = info_csv.readline().split(",", num_features)
            master_info[math.floor(i/num_indivs)][int(row[0])] = row[0:num_features]  #not sure why need to index whole array

    for w in range(num_workers):
        worker_info = np.empty((num_workers, gens, num_indivs, num_features))

        with open(dirr + "/" + str(w) + "/info.csv", 'r') as info_csv:
            next(info_csv)

            for i in range(num_indivs * gens):
                row = info_csv.readline().split(",", num_features)
                print(w,math.floor(i / num_indivs),int(row[0]))
                worker_info[w][math.floor(i / num_indivs)][int(row[0])] = row[0:num_features]  # not sure why need to index whole array



    return master_info, worker_info, titles



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
    dirr = "/Users/Crbn/Desktop/McG Fall '16/EvoNets/evoNet/work_space/data/output/fitness_test2"

    param_plots(dirr, 8, 2000, .1, 40)
    #(dirr, num_workers, gens, output_freq, num_indivs)
