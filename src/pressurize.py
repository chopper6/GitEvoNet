import math
import reducer, solver, fitness
from ctypes import cdll

def pressurize(configs, net):
    # configs:
    pressure = math.ceil((float(configs['PT_pairs_dict'][1][0]) / 100.0))
    tolerance = configs['PT_pairs_dict'][1][1]
    sampling_rounds = int(configs['sampling_rounds'])
    max_sampling_rounds = int(configs['sampling_rounds_max'])
    knapsack_solver = cdll.LoadLibrary(configs['KP_solver_binary'])
    fitness_type = int(configs['fitness_type'])

    leaf_fitness, hub_fitness, solo_fitness = 0,0,0

    num_samples_relative = min(max_sampling_rounds, len(net.nodes()) * sampling_rounds)
    pressure_relative = int(pressure * len(net.nodes()))

    kp_instances = reducer.reverse_reduction(net, pressure_relative, int(tolerance), num_samples_relative, configs['advice_upon'], configs['biased'], configs['BD_criteria'])

    for kp in kp_instances:
        a_result = solver.solve_knapsack(kp, knapsack_solver)

        #various characteristics of a result
        inst_leaf_fitness, inst_hub_fitness, inst_solo_fitness  = fitness.kp_instance_properties(a_result, fitness_type, len(net.nodes()), len(net.edges()))

        leaf_fitness += inst_leaf_fitness
        hub_fitness += inst_hub_fitness
        solo_fitness += inst_solo_fitness

    leaf_fitness /= num_samples_relative
    hub_fitness /= num_samples_relative
    solo_fitness /= num_samples_relative

    return [leaf_fitness, hub_fitness, solo_fitness]


