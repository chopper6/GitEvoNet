import sys, os, time, math, networkx as nx
sys.path.insert(0, os.getenv('lib'))
import util

#--------------------------------------------------------------------------------------------------
def load_sim_configs (param_file, rank, num_workers):
    parameters = (open(param_file,'r')).readlines()
    assert len(parameters)>0
    configs = {}
    for param in parameters:
        if len(param) > 0: #ignore empty lines
            if param[0] != '#': #ignore lines beginning with #
                param = param.split('=')
                if len (param) == 2:
                    key   = param[0].strip().replace (' ', '_')
                    value = param[1].strip()
                    configs[key] = value

    configs['KP_solver_name']      = configs['KP_solver_binary'].split('/')[-1].split('.')[0]
    configs['timestamp']           = time.strftime("%B-%d-%Y-h%Hm%Ms%S")
    configs ['output_directory'] += "/"

    #kp_only, stamp may need work
    configs['instance_file'] = (util.slash(configs['output_directory'])) + "instances/" # + configs['stamp']) #TODO: 'stamp' needs to be redone is wanted

    #--------------------------------------------

    if rank == 0: #only master should create dir, prevents workers from fighting over creating the same dir
        while not os.path.isdir (configs['output_directory']):
            try:
                os.makedirs (configs['output_directory']) # will raise an error if invalid path, which is good
            except:
                time.sleep(5)
                continue

        if (configs['number_of_workers'] != num_workers): util.cluster_print(configs['output_directory'],"\nWARNING in init.load_sim_configs(): mpi #workers != config #workers! " + str(configs['number_of_workers']) + " vs " + str(num_workers) + "\n")  # not sure why this doesn't correctly get # config workers...

    return configs
#--------------------------------------------------------------------------------------------------  
def load_network (configs):    
    edges_file = open (configs['network_file'],'r') #note: with nx.Graph (undirected), there are 2951  edges, with nx.DiGraph (directed), there are 3272 edges
    M=nx.DiGraph()     
    next(edges_file) #ignore the first line
    for e in edges_file: 
        interaction = e.split()
        assert len(interaction)>=2
        source, target = str(interaction[0]).strip().replace("'",'').replace('(','').replace(')',''), str(interaction[1]).strip().replace("'",'').replace('(','').replace(')','')
        if (len(interaction) >2):
            if (str(interaction[2]) == '+'):
                Ijk=1
            elif  (str(interaction[2]) == '-'):
                Ijk=-1
            else:
                print ("Error: bad interaction sign in file "+str(edges_file)+"\nExiting...")
                sys.exit()
        else:
            Ijk=util.flip()     
        M.add_edge(source, target, sign=Ijk)    

    return M
#--------------------------------------------------------------------------------------------------
def build_advice(net, configs):
    if (configs['advice_creation'] == 'once'):
        #assumes no growth
        advice_upon = configs['advice_upon']
        biased = util.boool(configs['biased'])
        bias_on = str(configs['bias_on'])
        pressure = math.ceil((float(configs['PT_pairs_dict'][1][0]) / 100.0))
        samples, sample_size = None, None

        if (advice_upon == 'nodes'):
            samples = net.nodes()
            sample_size = int(pressure * len(net.nodes()))
        elif (advice_upon == 'edges'):
            samples = [[str(node_i), str(node_j)] for node_i in net.nodes() for node_j in net.nodes()]  # all possible edges
            #samples = net.edges()
            sample_size = int(pressure * len(net.edges())) #sample size based on all existing edges
        advice = util.advice (net, util.sample_p_elements(samples,sample_size), biased, advice_upon, bias_on)
    else: advice = None #will generate during reduction each time instead

    return advice