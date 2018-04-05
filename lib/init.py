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
    configs['num_workers'] = num_workers

    #kp_only, stamp may need work
    configs['datapoints_dir'] = configs['output_directory'] + "02_raw_instances_simulation/data_points/"
    configs['instance_file'] = (util.slash(configs['output_directory'])) + "instances/" # + configs['stamp']) #TODO: 'stamp' needs to be redone is wanted

    #--------------------------------------------
    #PT pairs aren't generally used for this version, but could be useful
    ALL_PT_pairs = {}
    ALL_PT_pairs[1] = (configs['pressure'],configs['tolerance'])

    completed_pairs                = []
    if os.path.isdir (configs['datapoints_dir']):
        for r,ds,fs in os.walk(configs['datapoints_dir']):
            RAW_FILES       = [f for f in fs if 'RAW' in f]            
            for raw_file in RAW_FILES:
                split = raw_file.split('_')
                p     = float(''.join([d for d in split[-8] if d.isdigit() or d=='.']))
                t     = float(''.join([d for d in split[-7] if d.isdigit() or d=='.']))
                completed_pairs.append((p,t))
    configs['PT_pairs_dict'] = {}
    for index in sorted(ALL_PT_pairs.keys()):
        if not ALL_PT_pairs[index] in completed_pairs:
            configs['PT_pairs_dict'][index] = ALL_PT_pairs[index]        
    #--------------------------------------------

    if rank == 0: #only master should create dir, prevents workers from fighting over creating the same dir
        while not os.path.isdir (configs['output_directory']):
            try:
                os.makedirs (configs['output_directory']) # will raise an error if invalid path, which is good
            except:
                time.sleep(5)
                continue

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