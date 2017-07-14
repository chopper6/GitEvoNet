import math
from decimal import Decimal
import reducer, solver, node_data, fitness, leaf_fitness as l_fitness
from ctypes import cdll
import numpy as np

def pressurize(configs, net, instance_file_name, advice):
    # configs:
    pressure = math.ceil((float(configs['PT_pairs_dict'][1][0]) / 100.0))
    tolerance = int(configs['PT_pairs_dict'][1][1])
    sampling_rounds = int(configs['sampling_rounds'])
    max_sampling_rounds = int(configs['sampling_rounds_max'])
    knapsack_solver = cdll.LoadLibrary(configs['KP_solver_binary'])
    advice_upon = configs['advice_upon']
    max_B_plot = int(configs['max_B_plot'])

    use_kp = configs['use_knapsack']

    leaf_metric = str(configs['leaf_metric'])
    leaf_operator = str(configs['leaf_operation'])
    leaf_pow = float(configs['leaf_power'])
    hub_metric = str(configs['hub_metric'])
    hub_operator = str(configs['hub_operation'])
    fitness_operator = str(configs['fitness_operation'])

    edge_assignment = str(configs['edge_state'])
    global_edge_bias = float(configs['global_edge_bias'])
    edge_distribution = str(configs['edge_state_distribution'])
    biased = str(configs['biased'])

    num_samples_relative = min(max_sampling_rounds, len(net.nodes()) * sampling_rounds)
    num_samples_relative = max(10, int(len(net.nodes())/10))
    if (advice_upon =='nodes'):
        pressure_relative = int(pressure * len(net.nodes()))
    elif (advice_upon =='edges'):
        pressure_relative = int(pressure * len(net.edges()))
    else:
        print("ERROR in pressurize(): unknown advice_upon: " + str(advice_upon))
        return


    if (use_kp == 'True' or use_kp == True):
        leaf_fitness, hub_fitness, solo_fitness = 0, 0, 0
        node_data.reset_fitness(net) #not actually used when kp = True
        node_data.reset_BDs(net)

        kp_instances = reducer.reverse_reduction(net, pressure_relative, tolerance, num_samples_relative, configs['advice_upon'], configs['biased'], configs['BD_criteria'], configs['bias_on'], advice)

        if (instance_file_name != None): open(instance_file_name, 'w')

        for kp in kp_instances:
            a_result = solver.solve_knapsack(kp, knapsack_solver)
            inst_leaf_fitness, inst_hub_fitness, inst_solo_fitness = fitness.kp_instance_properties(a_result, leaf_metric, leaf_operator, leaf_pow, hub_metric, hub_operator, fitness_operator, net, instance_file_name)

            leaf_fitness += inst_leaf_fitness
            hub_fitness += inst_hub_fitness
            solo_fitness += inst_solo_fitness

        leaf_fitness /= num_samples_relative
        hub_fitness /= num_samples_relative
        solo_fitness /= num_samples_relative


        return [leaf_fitness, hub_fitness, solo_fitness]

    elif (use_kp == 'False' or use_kp == False):

        #TODO: keep working on this
        if (edge_assignment == 'probabilistic'):
            # assumes no conservation score or global bias, and bernouille pr distribution
            # global bias: change prBD
            # local bias (consv score)...? calc base prBD sep, then for each node or something
            degrees = list(net.degree().values())
            degs, freqs = np.unique(degrees, return_counts=True)
            tot = float(sum(freqs))
            freqs = [(f / tot) * 100 for f in freqs]

            if (biased == True):
                p = global_edge_bias
                if (global_edge_bias < 0 or global_edge_bias > 1):
                    print("ERROR in pressurize: out of bounds global_edge_bias")
                    p = .5
            else: p = .5

            fitness_score = 1

            for i in range(len(degs)):
                deg_fitness = 0
                for B in range(degs[i]):
                    D = degs[i] - B
                    prBD = (math.factorial(B + D) / (math.factorial(B) * math.factorial(D))) * math.pow(p, B) * math.pow(1-p, D)
                    assert (prBD >= 0 and prBD <= 1)
                    fitBD = l_fitness.node_score(leaf_metric, B, D)
                    deg_fitness += prBD * fitBD
                fitness_score *= math.pow(deg_fitness,freqs[i]) #as per node product rule

                #reducer.prob_reduction(net, global_edge_bias, edge_distribution, configs['biased'], configs['bias_on'])

        elif (edge_assignment == 'experience'):
            node_data.reset_fitness(net)
            for i in range(num_samples_relative):
                node_data.reset_BDs(net)
                reducer.exp_reduction(net, pressure_relative, tolerance, num_samples_relative, configs['advice_upon'], configs['biased'], configs['BD_criteria'], configs['bias_on'])
                fitness.node_fitness(net, leaf_metric)

            fitness.node_normz(net, num_samples_relative)
            if (fitness_operator == 'product'): fitness_score = Decimal(fitness.node_product(net))
            elif (fitness_operator == 'entropy'): fitness_score = Decimal(fitness.node_entropy(net))
            else: print("Error in pressurize(): unknown fitness_op: " + str(fitness_operator))

        return [0,0, fitness_score] #weird as all hell, but [2] is used as the actual fitness


    else: print("ERROR in pressurize(): unknown use_knapsack config: " + str(use_kp))
