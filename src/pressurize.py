import math
import reducer, solver
from time import process_time as ptime

def pressurize(configs, net, pressure_relative, tolerance, knapsack_solver, fitness_type, num_samples_relative):
    #TODO: parse into at least 2 fns
    #does all the reducing to kp and solving
    #how can it call configs without being passed???
    RGGR, ETB = 0, 0
    dist_in_sack = 0
    dist_sq_in_sack = 0

    ETB_ratio = 0
    RGAllR = 0
    t0 = ptime()
    kp_instances = reducer.reverse_reduction(net, pressure_relative, int(tolerance), num_samples_relative, configs['advice_upon'], configs['biased'], configs['BD_criteria'])
    t1 = ptime()
    reducer_time = t1-t0   
    solver_time = 0
    crunch_time = 0

    for kp in kp_instances:
        t0 = ptime()
        a_result = solver.solve_knapsack(kp, knapsack_solver)
        t1 = ptime()
        solver_time += t1-t0
      
        t0 = ptime()

        #parse_result(a_result, fitness_type)

        #various characteristics of a result
        instance_RGGR, instance_ETB,inst_dist_in_sack, inst_dist_sq_in_sack, inst_ETB_ratio, inst_RGAllR  = 0,0,0,0,0,0

        # the solver returns the following as a list:
        # 0		GENES_in: 		a list, each element in the list is a tuple of three elements: node(gene) ID, its value(benefit), its weight(damage)
        # 1     number_green_genes
        # 2     number_red_genes
        # 3     number_grey genes

        if len(a_result) > 0:
            Gs, Bs, Ds, Xs = [], [], [], []
            # -------------------------------------------------------------------------------------------------
            #GENES_in, GENES_out, coresize, execution_time = a_result[4], a_result[5], a_result[9], a_result[10]

            GENES_in, num_green, num_red, num_grey = a_result[0], a_result[1], a_result[2], a_result[3]
            # -------------------------------------------------------------------------------------------------
            soln_bens = []
            for g in GENES_in:

                # g[0] gene name
                # g[1] benefits
                # g[2] damages
                # g[3] if in knapsack (binary)

                #hub score eval pt1
                inst_dist_in_sack += abs(g[1] - g[2])
                inst_dist_sq_in_sack += math.pow((g[1] - g[2]), 2)
                soln_bens.append(g[1])

            #hub score eval pt2
            instance_ETB = sum(set(soln_bens))
            if (sum(soln_bens) != 0): inst_ETB_ratio = sum(set(soln_bens))/sum(soln_bens)
            else: inst_ETB_ratio = sum(set(soln_bens))

            #leaf score eval
            if (num_grey != 0):
                instance_RGGR = (num_green + num_red) / num_grey
            else:
                instance_RGGR = (num_green + num_red)
            inst_RGAllR = (num_green + num_red) / (num_green + num_red + num_grey)

        else:
            print ("WARNING in pressurize(): no results from oracle advice")

        ETB += instance_ETB
        RGGR += instance_RGGR
        dist_in_sack += inst_dist_in_sack
        dist_sq_in_sack += inst_dist_sq_in_sack
        ETB_ratio += inst_ETB_ratio
        RGAllR += inst_RGAllR
 
        t1 = ptime()
        crunch_time += t1-t0

    ETB /= num_samples_relative
    RGGR /= num_samples_relative
    dist_in_sack /= num_samples_relative
    dist_sq_in_sack /= num_samples_relative
    ETB_ratio /= num_samples_relative
    RGAllR /= num_samples_relative

    #print("Pressurize time: \t reducer: " + str(reducer_time) + " \t solver: " + str(solver_time) + " \t crunch: " + str(crunch_time))

    if (fitness_type == 0 or fitness_type == 1 or fitness_type == 2):
        return [RGGR, ETB]
    elif (fitness_type == 3 or fitness_type == 4 or fitness_type == 5):
        return [RGAllR, ETB]
    elif (fitness_type == 6 or fitness_type == 7 or fitness_type == 8):
        return [RGGR, dist_in_sack]
    elif (fitness_type == 9 or fitness_type == 10 or fitness_type == 11):
        return [RGAllR, dist_in_sack]
    elif (fitness_type == 12 or fitness_type == 13 or fitness_type == 14): #doesn't work at all
        node_to_edge_ratio = len(net.nodes())/len(net.edges())
        return [node_to_edge_ratio, dist_in_sack]
    else: print("ERROR in pressurize(): unknown fitness type.")
