#!/usr/local/bin/python3
import os, csv, powerlaw
from scipy.stats import itemfreq


def init_csv(pop_size, num_workers, out_dir, configs):

    csv_title = "Net ID#, Net Size, Fitness, Leaf Measure,  Hub Measure, Average Degree\n"
    #, In-Degree Powerlaw Fit (vs Exponential) LogLikelihood Ratio, In-Degree Powerlaw Fit (vs Exponential) P-Value, In-Degree Powerlaw xmin, Out-Degree Powerlaw Fit (vs Exponential) LogLikelihood Ratio, Out-Degree Powerlaw Fit (vs Exponential) P-Value, Out-Degree Powerlaw xmin
    deg_distrib_title = "Net Size, In Degrees, In Degree Frequencies, Out Degrees, Out Degree Frequencies\n"

    with open(out_dir+"info.csv",'w') as csv_out:
        csv_out.write(csv_title)
    with open(out_dir+"degree_distrib.csv",'w') as csv_out:
        csv_out.write(deg_distrib_title) #just blanking the file

    out_configs = out_dir + "/configs_used.csv"

    with open(out_configs, 'w') as outConfigs:
        for config in configs:
            outConfigs.write(config + "," + str(configs[config]) + "\n")


def to_csv(population, output_dir):

    if (population[0].net.edges()):
        output_csv = output_dir + "/info.csv"

        with open(output_csv, 'a') as output_file:
            output = csv.writer(output_file)

            #maybe change to just the most fit in popn?
            for p in range(len(population)):
                net_info = []
                net_info.append(population[p].id)
                net_info.append(len(population[p].net.nodes()))
                net_info.append(population[p].fitness)
                #net_info.append(population[p].fitness_parts[0])
                net_info.append(population[p].fitness_parts[0])
                net_info.append(population[p].fitness_parts[1])
                net_info.append(sum(population[p].net.degree().values())/len(population[p].net.nodes()))

                '''
                in_degrees, out_degrees = list(population[0].net.in_degree().values()), list(population[0].net.out_degree().values())
                tmp = itemfreq(in_degrees)
                indegs, indegs_freqs = tmp[:, 0], tmp[:, 1]  # 0 = unique values in data, 1 = frequencies
                indeg_fit = powerlaw.Fit(indegs_freqs, discrete=True)
                indeg_xmin = indeg_fit.power_law.xmin
                indeg_loglikeli_ratio, indeg_pval = indeg_fit.distribution_compare('power_law', 'exponential')

                tmp = itemfreq(out_degrees)
                outdegs, outdegs_freqs = tmp[:, 0], tmp[:, 1]  # 0 = unique values in data, 1 = frequencies
                outdeg_fit = powerlaw.Fit(outdegs_freqs)
                outdeg_xmin = outdeg_fit.power_law.xmin
                outdeg_loglikeli_ratio, outdeg_pval = outdeg_fit.distribution_compare('power_law', 'exponential')

                net_info.append(indeg_loglikeli_ratio)
                net_info.append(indeg_pval)
                net_info.append(indeg_xmin)

                net_info.append(outdeg_loglikeli_ratio)
                net_info.append(outdeg_pval)
                net_info.append(outdeg_xmin)
                '''

                output.writerow(net_info)
                #write rows more concisely?

        with open(output_dir + "/degree_distrib.csv", 'a') as deg_file:
                #only distribution of most fit net
                output = csv.writer(deg_file)

                distrib_info = []
                distrib_info.append(len(population[0].net.nodes()))

                in_degrees, out_degrees = list(population[0].net.in_degree().values()), list(population[0].net.out_degree().values())

                tmp = itemfreq(in_degrees)
                indegs, indegs_freqs = tmp[:, 0], tmp[:, 1]  # 0 = unique values in data, 1 = frequencies
                distrib_info.append(indegs)
                distrib_info.append(indegs_freqs)

                tmp = itemfreq(out_degrees)
                outdegs, outdegs_freqs = tmp[:, 0], tmp[:, 1]
                distrib_info.append(outdegs)
                distrib_info.append(outdegs_freqs)

                output.writerow(distrib_info)
