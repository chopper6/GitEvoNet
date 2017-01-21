#!/usr/bin/python3
import os,sys
os.environ['lib'] = "/home/2014/choppe1/Documents/EvoNet/virt_workspace/lib"
sys.path.insert(0, os.getenv('lib'))
import util, init, master



def batch_run(dirr):
    #ASSUMES all files in dirr are config files
    for config_file in os.listdir(dirr):
        print("Starting evo of config file: " + str(config_file))
        configs = init.initialize_master(dirr+"/"+config_file, 0)
        master.evolve_master(configs)
    print("Batch run completed.")



def single_run(config_file):
    #config_file         = util.getCommandLineArgs ()
    configs             = init.initialize_master (config_file, 0)

    #master.evolve_master_sequential_debug(configs)
    master.evolve_master(configs)



if __name__ == "__main__":

    dirr = sys.argv[1]
    print("Harvesting config files from directory: " + str(dirr))
    batch_run(dirr)

    #single_run(dirr)

