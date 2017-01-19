#!/usr/bin/python3
import os,sys
os.environ['lib'] = "/home/2014/choppe1/Documents/EvoNet/virt_workspace/lib"
sys.path.insert(0, os.getenv('lib'))
import util, master


if __name__ == "__main__":

    config_file         = util.getCommandLineArgs ()
    M, configs          = init.initialize_master (config_file, 0)

    #master.evolve_master_sequential_debug(configs)
    master.evolve_master(configs)
