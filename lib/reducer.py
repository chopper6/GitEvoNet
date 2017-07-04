import random, util, math, time, numpy as np

#--------------------------------------------------------------------------------------------------
def reverse_reduction(net, sample_size, T_percentage, advice_sampling_threshold, advice_upon, biased, BD_criteria, bias_on):
    if  advice_sampling_threshold <=0:
        print ("WARNING: simple_reduction yields empty set.")
        yield [{},{},0]
    else:
        if (advice_upon == 'nodes'): samples = net.nodes()
        elif (advice_upon == 'edges'): samples = net.edges()
        else:
            print ("ERROR reverse_reduction: unknown advice_upon: " + str(advice_upon))
            return

        for i in range(advice_sampling_threshold):
            yield [ BDT_calculator   (net, util.advice (net, util.sample_p_elements(samples,sample_size), biased, advice_upon, bias_on), T_percentage, BD_criteria, advice_upon) ]


#--------------------------------------------------------------------------------------------------  
def exp_reduction(net, sample_size, T_percentage, advice_sampling_threshold, advice_upon, biased, BD_criteria, bias_on):
    #print ("in reducer, " + str(advice_sampling_threshold))
    if  advice_sampling_threshold <=0:
        print ("WARNING: reverse_reduction yields empty set.")
        Bs,Ds, tol = [{},{},0]
    else:
        if (advice_upon == 'nodes'): samples = net.nodes()
        elif (advice_upon == 'edges'): samples = net.edges()
        else:
            print ("ERROR reverse_reduction: unknown advice_upon: " + str(advice_upon))
            return

        Bs,Ds,tol = BDT_calculator   (net, util.advice (net, util.sample_p_elements(samples,sample_size), biased, advice_upon,bias_on), T_percentage, BD_criteria, advice_upon)
    return Bs,Ds,tol



# --------------------------------------------------------------------------------------------------
def prob_reduction(net, global_ben_bias, distribn, biased, biased_on):
    # assumes advice on edges

    for edge in net.edges():
        source, target = edge[0], edge[1]
        if (biased == True and biased_on == 'edges'): indiv_bias = net[source][target]['conservation_score']
        elif (biased == True and biased_on == 'nodes'): indiv_bias = (net.node[source]['conservation_score'] + net.node[target]['convservation_score']) / 2
        else: indiv_bias = 0

        ben_pr = None
        if (distribn == 'set'): ben_pr = .5 + global_ben_bias
        if (distribn == 'uniform'): ben_pr = random.uniform(0,1) + global_ben_bias #same as rd.random() i think
        elif (distribn == 'normal'):
            ben_pr = random.normalvariate(0, 1)
            ben_pr = (ben_pr + .5)/2 + global_ben_bias

        edge_ben = ben_pr + indiv_bias
        if (edge_ben > 1): edge_ben=1
        elif (edge_ben < 0): edge_ben=0
        for side in [source, target]:
            net.node[side]['benefits'] = edge_ben
            net.node[side]['damages'] = 1-edge_ben


#--------------------------------------------------------------------------------------------------
def BDT_calculator (M, Advice, T_percentage, BD_criteria, advice_upon):
    BENEFITS, DAMAGES = {}, {}

    if (BD_criteria != 'both' and BD_criteria != 'source' and BD_criteria != 'target'):
        print("ERROR in reducer.BDT_calc_node: unknown BD_criteria: " + str(BD_criteria))
    
    for element in Advice.keys():
        if (advice_upon=='nodes'): #TODO: add node advice version, if nec
            target = element
            sources = M.predecessors(target)

            for source in sources:
                advice = Advice[target]

                if M[source][target]['sign']==advice:      #in agreement with the Oracle
                    if (BD_criteria == 'both' or BD_criteria == 'source'):
                        ######### REWARDING the source node ###########
                        if source in BENEFITS.keys():
                            BENEFITS[source]+=1
                        else:
                            BENEFITS[source]=1
                            if source not in DAMAGES.keys():
                                DAMAGES[source]=0

                    if (BD_criteria == 'both' or BD_criteria == 'target'):
                        ######### REWARDING the target node ###########
                        if target in BENEFITS.keys():
                            BENEFITS[target]+=1
                        else:
                            BENEFITS[target]=1
                            if target not in DAMAGES.keys():
                                DAMAGES[target]=0

                ###############################################
                else:                                              #in disagreement with the Oracle
                    if (BD_criteria == 'both' or BD_criteria == 'source'):
                        ######### PENALIZING the source node ##########
                        if source in DAMAGES.keys():
                            DAMAGES[source]+=1
                        else:
                            DAMAGES[source]=1
                            if source not in BENEFITS.keys():
                                BENEFITS[source]=0

                    if (BD_criteria == 'both' or BD_criteria == 'target'):
                        ######### PENALIZING the target node ##########
                        if target in DAMAGES.keys():
                            DAMAGES[target]+=1
                        else:
                            DAMAGES[target]=1
                            if target not in BENEFITS.keys():
                                BENEFITS[target]=0
                    ###############################################

        elif (advice_upon=='edges'):
            advice = Advice[element]
            element = element.replace('(','').replace(')','').replace("'",'').replace(' ','')
            element = element.split(",")
            source = int(element[0])
            target = int(element[1])
            if M[source][target]['sign'] == advice:  # in agreement with the Oracle
                if (BD_criteria == 'both' or BD_criteria == 'source'):
                    ######### REWARDING the source node ###########
                    M.node[source]['benefits'] += 1
                    if source in BENEFITS.keys():
                        BENEFITS[source] += 1
                    else:
                        BENEFITS[source] = 1
                        if source not in DAMAGES.keys():
                            DAMAGES[source] = 0


                if (BD_criteria == 'both' or BD_criteria == 'target'):
                    ######### REWARDING the target node ###########
                    M.node[target]['benefits'] += 1
                    if target in BENEFITS.keys():
                        BENEFITS[target] += 1
                    else:
                        BENEFITS[target] = 1
                        if target not in DAMAGES.keys():
                            DAMAGES[target] = 0

            ###############################################
            else:  # in disagreement with the Oracle
                if (BD_criteria == 'both' or BD_criteria == 'source'):
                    ######### PENALIZING the source node ##########
                    M.node[source]['damages'] += 1
                    if source in DAMAGES.keys():
                        DAMAGES[source] += 1
                    else:
                        DAMAGES[source] = 1
                        if source not in BENEFITS.keys():
                            BENEFITS[source] = 0

                if (BD_criteria == 'both' or BD_criteria == 'target'):
                    ######### PENALIZING the target node ##########
                    M.node[target]['damages'] += 1
                    if target in DAMAGES.keys():
                        DAMAGES[target] += 1
                    else:
                        DAMAGES[target] = 1
                        if target not in BENEFITS.keys():
                            BENEFITS[target] = 0
                            ###############################################

        else:
            print ("ERROR reducer: unknown advice_upon: " + str(advice_upon))
            return
    
    T_edges = round (max (1, math.ceil (sum(DAMAGES.values())*(T_percentage/100))))

    assert len(BENEFITS.keys())==len(DAMAGES.keys())
    return BENEFITS, DAMAGES, T_edges
