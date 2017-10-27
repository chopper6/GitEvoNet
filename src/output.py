#!/usr/local/bin/python3
import os, csv, math
#from scipy.stats import itemfreq
import numpy as np
np.set_printoptions(formatter={'int_kind': lambda x:' {0:d}'.format(x)})
import networkx as nx


def init_csv(out_dir, configs):
 
    csv_title = "Generation, Net Size, Fitness, Leaf Measure,  Hub Measure, Solo Measure, Average Degree, Edge:Node Ratio, Mean Fitness, Variance in Fitness, Fitness_Div_#Edges, Fitness_Div_#Nodes\n"
    #csv_title = "Net Size, Fitness, Leaf Measure,  Hub Measure, Solo Measure, Average Degree, Edge:Node Ratio, Clustering Coefficient, # Triangle Communities\n"
    deg_distrib_title = "Generation, Net Size, In Degrees, In Degree Frequencies, Out Degrees, Out Degree Frequencies, Degs, Deg Freqs\n"

    deg_summary_title = "In Degrees, In Degree Frequencies, Out Degrees, Out Degree Frequencies\n"

    with open(out_dir+"/info.csv",'w') as csv_out:
        csv_out.write(csv_title)
    with open(out_dir+"/degree_distrib.csv",'w') as csv_out:
        csv_out.write(deg_distrib_title) #just blanking the file

    out_configs = out_dir + "/configs_used.csv"

    with open(out_configs, 'w') as outConfigs:
        #keys = configs.keys()
        #keys.sort()
        for config in configs:
            outConfigs.write(config + "," + str(configs[config]) + "\n")

    out_time = out_dir + "/timing.csv"
    with open(out_time, 'w') as out_timing:
        out_timing.write("Net Size, Presssurize Time\n")


    out_deg_summary = out_dir + "/degree_change.csv"
    with open(out_deg_summary, 'w') as out_summary:
        out_summary.write(deg_summary_title)


def deg_change_csv(population, output_dir):
    with open(output_dir + "/degree_change.csv", 'a') as deg_file:
        # only distribution of most fit net
        output = csv.writer(deg_file)
        distrib_info = []

        degrees = list(population[0].net.degree().values())

        #is actually all degs not just in
        indegs, indegs_freqs = np.unique(degrees, return_counts=True)
        indegs = np.array2string(indegs).replace('\n', '')
        indegs_freqs = np.array2string(indegs_freqs).replace('\n', '')
        distrib_info.append(indegs)
        distrib_info.append(indegs_freqs)

        output.writerow(distrib_info)


def popn_data(population, output_dir, gen):

    if (population[0].net.edges()):
        output_csv = output_dir + "/info.csv"

        with open(output_csv, 'a') as output_file:
            output = csv.writer(output_file)

            all_fitness = np.array([population[p].fitness for p in range(len(population))])
            mean_fitness = np.mean(all_fitness)
            var_fitness = np.var(all_fitness)

            Net = population[0] #most fit net
            net = Net.net
            nets_info = [gen, len(net.nodes()), Net.fitness, Net.fitness_parts[0], Net.fitness_parts[1], Net.fitness_parts[2], sum(net.degree().values())/len(net.nodes()),len(net.edges())/len(net.nodes()), mean_fitness, var_fitness, Net.fitness/float(len(net.edges())), Net.fitness/float(len(net.nodes()))]

            output.writerow(nets_info)

        with open(output_dir + "/degree_distrib.csv", 'a') as deg_file:
            #only distribution of most fit net
            output = csv.writer(deg_file)

            distrib_info = []
            distrib_info.append(gen)
            distrib_info.append(len(population[0].net.nodes()))

            in_degrees, out_degrees = list(population[0].net.in_degree().values()), list(population[0].net.out_degree().values())

            indegs, indegs_freqs = np.unique(in_degrees, return_counts=True)
            indegs = np.array2string(indegs).replace('\n', '')
            indegs_freqs = np.array2string(indegs_freqs).replace('\n', '')
            #tmp = itemfreq(in_degrees)
            #indegs, indegs_freqs = tmp[:, 0], tmp[:, 1]  # 0 = unique values in data, 1 = frequencies
            distrib_info.append(indegs)
            distrib_info.append(indegs_freqs)

            outdegs, outdegs_freqs = np.unique(out_degrees, return_counts=True)
            outdegs = np.array2string(outdegs).replace('\n', '')
            outdegs_freqs = np.array2string(outdegs_freqs).replace('\n', '')
            #tmp = itemfreq(out_degrees)
            #outdegs, outdegs_freqs = tmp[:, 0], tmp[:, 1]
            distrib_info.append(outdegs)
            distrib_info.append(outdegs_freqs)

            degrees = list(net.degree().values())
            degs, freqs = np.unique(degrees, return_counts=True)
            distrib_info.append(degs)
            distrib_info.append(freqs)

            output.writerow(distrib_info)


def minion_csv(output_dir, pressurize_time, num_growth, end_size):
    if (num_growth == 0): num_growth = 1
    with open(output_dir + "/timing.csv", 'a') as time_file:
        output=csv.writer(time_file)
        info = []
        info.append(end_size)
        pressurize_time = pressurize_time/num_growth
        info.append(pressurize_time)
        output.writerow(info)
