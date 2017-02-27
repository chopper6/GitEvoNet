import sys, random
#--------------------------------------------------------------------------------------------------
def getCommandLineArgs():
    if len(sys.argv) < 2:
        print ("Usage: python3 test.py [/absolute/path/to/configs/file.txt]\nExiting..\n")
        sys.exit()
    return str(sys.argv[1])
#----------------------------------------------------------------------------  
def slash(path):
    return path+(path[-1] != '/')*'/'
#--------------------------------------------------------------------------------------------------
def flip():
    return random.choice([1,-1])
    #return random.SystemRandom().choice([1,-1])
#--------------------------------------------------------------------------------------------------
def sample_p_elements (elements,p):
    #elements = nodes or edges
    return  random.sample(elements,p)
    #return  random.SystemRandom().sample(elements,p) 
#--------------------------------------------------------------------------------------------------
def advice (M, samples, biased, advice_upon):
    advice = {}
    if not biased:
        for element in samples:
            advice[element]=flip()
    else:
        for element in samples:
            if (advice_upon=='nodes'):  biased_center = 0.5 + M.node[element]['conservation_score']
            elif (advice_upon == 'edges'):  biased_center = 0.5 + M.edge[element]['conservation_score']
            else:
                print("ERROR util.advice(): unknown advice_upon: " + str(advice_upon))
                return

            rand                = random.uniform(0,1)
            #rand                = random.SystemRandom().uniform(0,1)
            if rand <= biased_center:
                advice[element] = 1    #should be promoted (regulation) or conserved (evolution)
            else:
                advice[element] = -1   #should be inhibited (regulation) or deleted (evolution)
    
    return advice
#--------------------------------------------------------------------------------------------------
