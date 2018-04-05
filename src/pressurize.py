import math
import reducer, solver, node_data, fitness, util, probabilistic_entropy
from ctypes import cdll

def pressurize(configs, net, instance_file_name, advice, BD_table):
    # configs:
    pressure = math.ceil((float(configs['PT_pairs_dict'][1][0]) / 100.0))
    sampling_rounds_multiplier = float(configs['sampling_rounds_multiplier']) #FRACTION of curr number of EDGES
    if (util.is_it_none(configs['sampling_rounds_max']) == None): max_sampling_rounds = None
    else: max_sampling_rounds = int(configs['sampling_rounds_max'])
    knapsack_solver = cdll.LoadLibrary(configs['KP_solver_binary'])
    advice_upon = configs['advice_upon']
    use_kp = util.boool(configs['use_knapsack'])
    leaf_metric = str(configs['leaf_metric'])
    leaf_pow = float(configs['leaf_power'])
    hub_metric = str(configs['hub_metric'])
    hub_operator = str(configs['hub_operation'])
    fitness_operator = str(configs['fitness_operation'])
    edge_state = str(configs['edge_state'])
    biased = util.boool(configs['biased'])

    scale_node_fitness = util.boool(configs['scale_node_fitness'])

    #num_samples_relative = min(max_sampling_rounds, len(net.nodes()) * sampling_rounds)
    num_samples_relative = max(1, int(len(net.edges())*sampling_rounds_multiplier) )
    if (max_sampling_rounds): num_samples_relative = min(num_samples_relative, max_sampling_rounds)

    if (advice_upon =='nodes'): pressure_relative = int(pressure * len(net.nodes()))
    elif (advice_upon =='edges'): pressure_relative = int(pressure * len(net.edges()))
    else:
        print("ERROR in pressurize(): unknown advice_upon: " + str(advice_upon))
        return


    if (use_kp == 'True' or use_kp == True):
        leaf_fitness, hub_fitness, solo_fitness = 0, 0, 0
        node_data.reset_fitness(net) #not actually used when kp = True
        node_data.reset_BDs(net)

        kp_instances = reducer.reverse_reduction(net, pressure_relative, num_samples_relative, advice, configs)


        if (instance_file_name != None): open(instance_file_name, 'w')

        for kp in kp_instances:
            a_result = solver.solve_knapsack(kp, knapsack_solver)
            inst_solo_fitness, inst_leaf_fitness, inst_hub_fitness = fitness.kp_instance_properties(a_result, leaf_metric, leaf_pow, hub_metric, hub_operator, fitness_operator, net, instance_file_name)
            leaf_fitness += inst_leaf_fitness
            hub_fitness += inst_hub_fitness
            solo_fitness += inst_solo_fitness

        leaf_fitness /= num_samples_relative
        hub_fitness /= num_samples_relative
        solo_fitness /= num_samples_relative

        net.fitness, net.leaf_fitness, net.hub_fitness = solo_fitness, leaf_fitness, hub_fitness

    elif (use_kp == 'False' or use_kp == False):
        #  assumes 100% pressure

        if (edge_state == 'probabilistic'):
            assert(not biased or not configs['bias_on']=='nodes')
            fitness_score = probabilistic_entropy.calc_fitness(net, BD_table, configs)

        elif (edge_state == 'experience'):
            node_data.reset_fitness(net)
            for i in range(num_samples_relative):
                node_data.reset_BDs(net)
                reducer.exp_BDs(net, configs)
                fitness.node_fitness(net, leaf_metric)

            fitness.node_normz(net, num_samples_relative)
            fitness_score = fitness.node_product(net, scale_node_fitness)

        else:
            print("ERROR in pressurize: Unknown edge state " + str(edge_state))
            return

        net.fitness = fitness_score

    else: print("ERROR in pressurize(): unknown use_knapsack config: " + str(use_kp))
