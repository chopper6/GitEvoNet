#!/usr/bin/python3
import os,sys
from mpi4py import MPI
os.environ['lib'] = "/home/2014/choppe1/Documents/EvoNet/virt_workspace/lib"
sys.path.insert(0, os.getenv('lib'))



def batch_run(dirr, num_workers):
    #ASSUMES all files in dirr are config files
    for config_file in os.listdir(dirr):
        print("Starting evo of config file: " + str(config_file))
        configs = init.initialize_master(dirr+"/"+config_file, 0)

        num_workers_configs = int(configs['number_of_workers'])
        if (num_workers != num_workers_configs): print("WARNING in evolve_root.batch_run(): inconsistent # of workers, using command line choice:" + str(num_workers) + ", instead of " + str(num_workers_configs))
        out_dir = dirr.replace('input','output')
        master.evolve_master(out_dir, configs, num_workers)
    print("Batch run completed.")



def single_run(config_file):
    #config_file         = util.getCommandLineArgs ()
    configs             = init.initialize_master (config_file, 0)
    master.evolve_master_sequential_debug(configs)
    #master.evolve_master(configs)



if __name__ == "__main__":

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    num_workers = comm.Get_size() - 1  # dont count master
    #arguments = sys.argv  # arguments should contain the /path/to/configs.txt
    dirr = sys.argv[1]
    if rank == 0: print("Harvesting config files from directory: " + str(dirr))

    if rank == 0:  # ie is master
        with open('root_mpi.log', 'w') as f:
            f.write('Im in dir ' + str(os.getcwd()) + ', dirr = ' + str(dirr) + ', num_workers = ' + str(num_workers))
            f.flush()
            f.close()
        import util, init, master
        batch_run(dirr, num_workers)

    else:
        out_dir = dirr.replace('input','output')
        import minion

        minion.work(out_dir, rank)
        # workers wait for workload from master, work, and finally dump their results for the master to harvest.
        # repeat; a worker exits when master gives it an empty workload


