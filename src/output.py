#!/usr/local/bin/python3
import os, csv, collections
import networkx as nx
import numpy as np
from scipy.stats import itemfreq
import plot_nets


def parallel_configs(ID, output_dir, param_names, param_vals, indices):

    title = ""
    for i in range(len(param_names)):
        if (param_names[i] != None):
            title += str(param_names[i])
    title += "\n"

    if not os.path.exists(output_dir + "/" + str(ID)):
        os.makedirs(output_dir+ "/" + str(ID))

    '''
    with open(output_dir + "/" + str(ID) + "/worker_configs.csv", 'w') as outfile:
        outfile.write(title)
        worker_params = []
        for i in range(len(param_vals)):
            if (param_vals[i] != [0]):
                worker_params.append(param_vals[i][indices[i]])
        for i in range(len(worker_params)):
            outfile.write(str(worker_params[i]))
    '''

def net(ID, indiv, out_dir):   #unused, maybe a remnant of parallel implm
    if (indiv.net.edges()):
        output_file = out_dir + "/net_" + str(ID) + ".txt"
        with open(output_file , 'wb') as outfile:
            nx.write_edgelist(indiv.net, output_file)

        info_file = out_dir + "/fitness" + str(ID) + ".txt"
        with open(info_file , 'w') as outfile:
            outfile.write(indiv.fitness + "," + indiv.fitness_parts[0] + "," + indiv.fitness_parts[1])


def net_for_degree_dist(ID, population, out_dir):
    #file name: net#/rebirth# - gen

    for p in range(len(population)):
        if (population[0].net.edges()):
            output_file = out_dir + "/net" + str(ID) +  "_" + str(len(population[p].net.nodes())) + ".txt"
            with open(output_file , 'w') as outfile:
                outfile.write("From\tTo\tSign\n")
                for edge in population[p].net.edges():
                    sign = population[p].net[edge[0]][edge[1]]['sign']
                    if (sign == 1): sign='+'
                    elif (sign== -1):   sign = '-'
                    else: print("ERROR output(): unknown sign")
                    formatted = str(edge[0]) + "\t" + str(edge[1]) + "\t" + str(sign) + "\n"
                    outfile.write(formatted)
                #nx.write_edgelist(population[p].net, output_file)  #prob faster, but doesn't match degree_dist.py expectation

def init_csv(pop_size, num_workers, out_dir, configs):

    csv_title = "Net ID#, Net Size, Fitness (Ben Dmg dist), Red-Green to Grey Ratio, Effective Total Benefits, Average Degree\n"
        #OLD: "Net ID#, Net Size, Fitness, Red-Green to Grey Ratio, Effective Total Benefits, ETB Heuristic, Average Degree\n"
    #csv_popn_title = "Net Size, Max Fitness, Min Fitness, Max Red-Green to Grey Ratio, Min Red-Green to Grey Ratio, Max Effective Total Benefits, Min Effective Total Benefits, Max  Average Degree, Min  Average Degree\n"
    deg_distrib_title = "Net Size, In Degrees, In Degree Frequencies, Out Degrees, Out Degree Frequencies\n"
    configs_title = "Pressure,Tolerance,Max Sampling Rounds, Generations, Population Size, Percent Survive, Mutation Bias, Mutation Frequency, Crossover Frequency, Crossover Percent, Starting Size, Output Frequency, Growth Frequency, Fitness Type\n"
    #["num_workers", "gens", "num_survive", "crossover_percent", "crossover_freq", "grow_freq", "mutation_freq",  "mutation_bias", "output_dir",  "pressure", "tolerance", "fitness_hist_freq", "avg_degree"]

    if not os.path.exists(out_dir+"/master/"):
        os.makedirs(out_dir+"/master/")
        with open(out_dir+"/master/info.csv",'w') as csv_out:
            csv_out.write(csv_title)

    for w in range(num_workers):

        worker_dir = out_dir + "/" + str(w) + "/"
        if not os.path.exists(worker_dir):
            os.makedirs(worker_dir)
        if not os.path.exists(worker_dir + "/net"):
            os.makedirs(worker_dir + "/net")
        with open(worker_dir+"info.csv", 'w') as csv_out:
            csv_out.write(csv_title)
        #with open(worker_dir + "population_info.csv", 'w') as popn_out:
            #popn_out.write(csv_popn_title)
        with open(worker_dir + "/degree_distrib.csv", 'w') as deg_out:
            deg_out.write(deg_distrib_title)

    '''
    for p in range(pop_size):
        out_csv = out_dir + "/info_" + str(p) + ".csv"
        with open(out_csv, 'w') as outCsv:
            outCsv.write("Gen,Size,Parent1,Parent2,Rank,Fitness,Red-Green/Grey Ratio,Effective Total Benefits,Solution Sum Benefits/Net Size, Degree Distribution\n")
    '''

    out_configs = out_dir + "/configs_used.csv"

    with open(out_configs, 'w') as outConfigs:
        outConfigs.write(configs_title)
        outConfigs.write(str(configs['pressure']) + "," + str(configs['tolerance']) + "," + str(configs['sampling_rounds_max']) + "," + str(configs['generations']) + "," + str(configs['population_size'])+ "," + str(configs['percent_survive']) + "," + str(configs['mutation_bias']) + "," + str(configs['mutation_frequency']) + "," + str(configs['crossover_frequency'])+ "," + str(configs['crossover_percent']) + "," + str(configs['starting_size']) + "," + str(configs['output_frequency']) + "," + str(configs['growth_frequency'])+ "," + str(configs["fitness_type"]) + "\n")



def to_csv(population, output_dir):
    #might need to format into matrix instead of single col
    #popn_info typically includes

    if (population[0].net.edges()):
        output_csv = output_dir + "/info.csv"

        '''
        with open(output_dir + "/population_info.csv", 'a') as popn_file:
            output = csv.writer(popn_file)
            row = []
            for i in range(len(popn_info)):
                row.append(popn_info[i])
            output.writerow(row)
        '''

        with open(output_csv, 'a') as output_file:
            output = csv.writer(output_file)

            #if (len(population[0].net.nodes()) != len(population[1].net.nodes())):
                #print("WARNING output(): nets are not same size. " + str(len(population[0].net.nodes())) + ", " + str(len(population[1].net.nodes())))

            for p in range(len(population)):
                net_info = []
                net_info.append(population[p].id)
                net_info.append(len(population[p].net.nodes()))
                net_info.append(population[p].fitness)
                #net_info.append(population[p].fitness_parts[0])
                net_info.append(population[p].fitness_parts[1])
                net_info.append(population[p].fitness_parts[2])
                net_info.append(sum(population[p].net.degree().values())/len(population[p].net.nodes()))
                output.writerow(net_info)
                #write rows more concisely?

        with open(output_dir + "/degree_distrib.csv", 'a') as deg_file:
                #only distribution of most fit net
                output = csv.writer(deg_file)

                distrib_info = []
                distrib_info.append(len(population[0].net.nodes()))

                in_nodes = []
                out_nodes = []

                in_degrees, out_degrees = list(population[0].net.in_degree().values()), list(population[0].net.out_degree().values())

                tmp = itemfreq(in_degrees)  # Get the item frequencies
                indegs, indegs_freqs = tmp[:, 0], tmp[:, 1]  # 0 = unique values in data, 1 = frequencies
                #print("output(): " + str(indegs) + "; " + str(indegs_freqs))
                distrib_info.append(indegs)
                distrib_info.append(indegs_freqs)

                tmp = itemfreq(out_degrees)  # Get the item frequencies
                outdegs, outdegs_freqs = tmp[:, 0], tmp[:, 1]  # 0 = unique values in data, 1 = frequencies
                distrib_info.append(outdegs)
                distrib_info.append(outdegs_freqs)

                output.writerow(distrib_info)


def outro_csv(output_dir, num_workers, gens, output_freq, num_indivs):
    #param_test lvl, not for indiv workers

    #generate max, min, and avg change of each feature in info.csv using numpy ndarray

    '''
    with open(output_dir + "/population_info.csv", 'r') as popn_file:
        titles = popn_file.readline().split(",")
        piece = titles[-1].split("\n")
        titles[-1] = piece[0]
        num_features = len(titles)

        lines = []
        for i in range(int(num_outs)):
            line = popn_file.readline().split(",")
            piece = line[-1].split("\n")
            line[-1] = piece[0]
            lines.append(line)

        avg_change = [0 for j in range(num_features+1)]

        for i in range(len(lines)-1):
            for j in range(num_features):
                avg_change[j] += (float(lines[i+1][j]) - float(lines[i][j])) / num_outs

            #spc to change in fitness, NOT generalized
            #where 1 is RGGR max and 3 is ETB max
            avg_change[-1] =  avg_change[1] + avg_change[3]
        for j in range(num_features+1):  #+1 for above added feature
            avg_change[j] /= len(lines)-1

    with open(output_dir + "/outro_info.csv", 'w') as outro_file:
        output = csv.writer(outro_file)
        row = []
        for j in range(num_features): #hopefully num_features in conserved from prev block
            row.append("Avg change of " + titles[j])
        row.append("Avg change in fitness")
        output.writerow(row)
        row = []
        for j in range(num_features+1): #+1 for added feature
            row.append(str(avg_change[j]))
        output.writerow(row)
    '''