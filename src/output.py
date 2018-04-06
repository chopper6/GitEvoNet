#!/usr/local/bin/python3
import csv, pickle
import numpy as np, networkx as nx
import util, pressurize, bias
np.set_printoptions(formatter={'int_kind': lambda x:' {0:d}'.format(x)})


def master_info(population, gen, size, pop_size, num_survive, advice, BD_table, configs):
    output_dir = configs['output_directory']
    num_output = int(configs['num_output'])
    num_net_output = int(configs['num_net_output'])
    max_gen = int(configs['max_generations'])
    num_instance_output = int(configs['num_instance_output'])
    instance_file = configs['instance_file']
    if (num_instance_output==0): instance_file = None

    if (gen % int(max_gen / num_output) == 0):
        popn_data(population, output_dir, gen)
        util.cluster_print(output_dir, "Master at gen " + str(gen) + ", with net size = " + str(size) + " nodes and " + str(len(population[0].net.edges())) + " edges, " + str(num_survive) + "<=" + str(len(population)) + " survive out of " + str(pop_size))
        nx.write_edgelist(population[0].net, output_dir + "/fittest_net.edgelist")

    if (num_instance_output != 0):
        if (gen % int(max_gen / num_instance_output) == 0):
            # if first gen, have already pressurized w/net[0]
            if (gen != 0): pressurize.pressurize(configs, population[0].net, instance_file + "Xitern" + str(gen) + ".csv", advice, BD_table)

    if (gen % int(max_gen / num_net_output) == 0):
        nx.write_edgelist(population[0].net, output_dir + "/nets/" + str(gen))
        pickle_file = output_dir + "/pickle_nets/" + str(gen) + "_pickle"
        with open(pickle_file, 'wb') as file:
            pickle.dump(population[0].net, file)



def final_master_info(population, gen, configs):
    output_dir = configs['output_directory']

    nx.write_edgelist(population[0].net, output_dir+"/nets/"+str(gen))
    pickle_file = output_dir + "/pickle_nets/" + str(gen) + "_pickle"
    with open(pickle_file, 'wb') as file: pickle.dump(population[0].net, file)
    popn_data(population, output_dir, gen)
    #draw_nets.basic(population, output_dir, total_gens)

    if util.boool(configs['biased']):
        util.cluster_print(output_dir,"Pickling biases.")
        bias.pickle_bias(population[0].net, output_dir+"/bias", configs['bias_on'])



def init_csv(out_dir, configs):
 
    csv_title = "Generation, Net Size, Fitness, Leaf Measure,  Hub Measure, Average Degree, Edge:Node Ratio, Mean Fitness, Variance in Fitness, Fitness_Div_#Edges, Fitness_Div_#Nodes\n"
    deg_distrib_title = "Generation, Net Size, In Degrees, In Degree Frequencies, Out Degrees, Out Degree Frequencies, Degs, Deg Freqs\n"

    deg_summary_title = "In Degrees, In Degree Frequencies, Out Degrees, Out Degree Frequencies\n"

    with open(out_dir+"/info.csv",'w') as csv_out:
        csv_out.write(csv_title)
    with open(out_dir+"/degree_distrib.csv",'w') as csv_out:
        csv_out.write(deg_distrib_title) #just blanking the file

    out_configs = out_dir + "/configs_used.csv"

    with open(out_configs, 'w') as outConfigs:
        for config in configs:
            outConfigs.write(config + "," + str(configs[config]) + "\n")

    out_time = out_dir + "/timing.csv"
    with open(out_time, 'w') as out_timing:
        out_timing.write("Net Size, Presssurize Time\n")


    out_deg_summary = out_dir + "/degree_change.csv"
    with open(out_deg_summary, 'w') as out_summary:
        out_summary.write(deg_summary_title)



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
            nets_info = [gen, len(net.nodes()), Net.fitness, Net.leaf_fitness, Net.hub_fitness, sum(net.degree().values())/len(net.nodes()),len(net.edges())/len(net.nodes()), mean_fitness, var_fitness, Net.fitness/float(len(net.edges())), Net.fitness/float(len(net.nodes()))]

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
            distrib_info.append(indegs)
            distrib_info.append(indegs_freqs)

            outdegs, outdegs_freqs = np.unique(out_degrees, return_counts=True)
            outdegs = np.array2string(outdegs).replace('\n', '')
            outdegs_freqs = np.array2string(outdegs_freqs).replace('\n', '')
            distrib_info.append(outdegs)
            distrib_info.append(outdegs_freqs)

            degrees = list(net.degree().values())
            degs, freqs = np.unique(degrees, return_counts=True)
            degs = np.array2string(degs).replace('\n', '')
            freqs = np.array2string(freqs).replace('\n', '')
            distrib_info.append(degs)
            distrib_info.append(freqs)

            output.writerow(distrib_info)

