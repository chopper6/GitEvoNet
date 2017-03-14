import math
import reducer, solver, fitness, node_fitness
from ctypes import cdll

def pressurize(configs, net, track_node_fitness):
    # configs:
    pressure = math.ceil((float(configs['PT_pairs_dict'][1][0]) / 100.0))
    tolerance = configs['PT_pairs_dict'][1][1]
    sampling_rounds = int(configs['sampling_rounds'])
    max_sampling_rounds = int(configs['sampling_rounds_max'])
    knapsack_solver = cdll.LoadLibrary(configs['KP_solver_binary'])
    num_samples_mult = int(configs['number_of_samples_multiplier'])
    advice = configs['advice_upon']
    max_B_plot = int(configs['max_B_plot'])

    leaf_metric = str(configs['leaf_metric'])
    hub_metric = str(configs['hub_metric'])
    fitness_operator = str(configs['fitness_operation'])

    leaf_fitness, hub_fitness, solo_fitness = 0,0,0

    num_samples_relative = min(max_sampling_rounds, len(net.nodes()) * sampling_rounds)
    num_samples_relative *= num_samples_mult
    if (advice=='nodes'): pressure_relative = int(pressure * len(net.nodes()))
    elif (advice=='edges'): pressure_relative = int(pressure * len(net.edges()))
    else: 
        print("ERROR in pressurize(): unknown advice_upon: " + str(advice))
        return

    kp_instances = reducer.reverse_reduction(net, pressure_relative, int(tolerance), num_samples_relative, configs['advice_upon'], configs['biased'], configs['BD_criteria'])
    if (track_node_fitness == True):
        node_info = node_fitness.gen_node_info(max_B_plot)
    else: node_info = None

    for kp in kp_instances:
        a_result = solver.solve_knapsack(kp, knapsack_solver)
        #various characteristics of a result
        node_info_instance = node_fitness.gen_node_info(max_B_plot)
        inst_leaf_fitness, inst_hub_fitness, inst_solo_fitness, node_info_instance  = fitness.kp_instance_properties(a_result, leaf_metric, hub_metric, fitness_operator, net, track_node_fitness, node_info_instance)
        if (track_node_fitness==True): node_info = node_fitness.add_instance(node_info, node_info_instance)

        leaf_fitness += inst_leaf_fitness
        hub_fitness += inst_hub_fitness
        solo_fitness += inst_solo_fitness

    #if (track_node_fitness == True): node_fitness.write_out(node_fitness_file, nodeFitness)

    leaf_fitness /= num_samples_relative
    hub_fitness /= num_samples_relative
    solo_fitness /= num_samples_relative

    if (track_node_fitness == True):
        node_info = node_fitness.normz(node_info, num_samples_relative, 'all')

    return [leaf_fitness, hub_fitness, solo_fitness, node_info]


