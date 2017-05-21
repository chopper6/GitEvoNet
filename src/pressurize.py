import math
import reducer, solver, node_data, fitness
from ctypes import cdll

def pressurize(configs, net, track_node_fitness, instance_file_name):
    # configs:
    pressure = math.ceil((float(configs['PT_pairs_dict'][1][0]) / 100.0))
    tolerance = int(configs['PT_pairs_dict'][1][1])
    sampling_rounds = int(configs['sampling_rounds'])
    max_sampling_rounds = int(configs['sampling_rounds_max'])
    knapsack_solver = cdll.LoadLibrary(configs['KP_solver_binary'])
    advice = configs['advice_upon']
    max_B_plot = int(configs['max_B_plot'])

    leaf_metric = str(configs['leaf_metric'])
    leaf_operator = str(configs['leaf_operation'])
    hub_metric = str(configs['hub_metric'])
    hub_operator = str(configs['hub_operation'])
    fitness_operator = str(configs['fitness_operation'])

    num_samples_relative = min(max_sampling_rounds, len(net.nodes()) * sampling_rounds)
    if (advice=='nodes'):
        pressure_relative = int(pressure * len(net.nodes()))
    elif (advice=='edges'):
        pressure_relative = int(pressure * len(net.edges()))
    else: 
        print("ERROR in pressurize(): unknown advice_upon: " + str(advice))
        return

    node_data.reset_fitness(net)

    for i in range(num_samples_relative):
        node_data.reset_BDs(net)
        reducer.simple_reduction(net, pressure_relative, tolerance, num_samples_relative, configs['advice_upon'], configs['biased'], configs['BD_criteria'])
        fitness.node_fitness(net, leaf_metric) #poss move this out of loop, ie sum all BDs first

    node_data.normz_by_num_instances(net, num_samples_relative)
    fitness_score = fitness.node_product(net)

    return fitness_score


