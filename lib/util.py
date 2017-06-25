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
def advice (M, samples, biased, advice_upon, bias_on):
    advice = {}
    if not biased:
        for element in samples:
            if (advice_upon=='nodes'): advice[element]=flip()
            elif (advice_upon=='edges'):
                advice[str(element)] = flip()

    else:
        for element in samples:
            if (advice_upon == 'nodes'):
                biased_center = M.node[element]['conservation_score']
            elif (advice_upon == 'edges'):
                ele = element
                source = int(ele[0])
                target = int(ele[1])
                if (bias_on == 'nodes'):
                    biased_center = (M.node[source]['conservation_score'] + M.node[target]['conservation_score'])/2
                elif (bias_on == 'edges'):
                    biased_center = M[source][target]['conservation_score']
                else: print("ERROR  util.advice(): unknown bias_on: " + str(bias_on))

            else:
                print("ERROR util.advice(): unknown advice_upon: " + str(advice_upon))
                return

            rand                = random.uniform(0,1)
            #rand                = random.SystemRandom().uniform(0,1)

            if (advice_upon=='nodes'): 
                if rand <= biased_center:            
                    advice[element] = 1
                else:
                    advice[element] = -1

            elif (advice_upon=='edges'):
                #if element not in advice.keys():
                    #advice[element] = {}
                    #print("UTIL.advice(): adding ele " + str(element) + " to advice.keys().")
                if rand <= biased_center:
                    advice[str(element)] = 1
                else:
                    advice[str(element)] = -1

    
    return advice
#--------------------------------------------------------------------------------------------------

def cluster_print(output_dir, text):
    with open(output_dir + "/thread_out.txt", 'a') as file:
        file.write(text + "\n")
        file.flush()
        file.close()


def cleanPaths(path):
    # ignore empty lines
    # ignore lines beginning with '#'
    # ignore lines enclosed by @ .. @
    # replaces $env_var with the actual value
    clean = []
    LINES = open(path,'r').readlines()
    inside_comment = False
    for i in range(len(LINES)):
        line = LINES[i].strip()
        if len(line)==0:
            continue
        if inside_comment:
            if line[0] == '@':
                inside_comment = False
        else:
            if line[0]=='@':
                inside_comment = True
                continue
            if line[0]!='#':
                clean.append(line)
    j=0
    for path in clean:
        Ds,i = path.split('/'), 0
        for d in Ds:
            if len(d.split('$'))>1:
                Ds[i]=os.getenv(d.split('$')[1])
            i+=1
        clean[j]='/'.join(Ds).replace('//','/')
        j+=1
    return clean