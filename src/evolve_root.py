#!/usr/bin/python3
import os,sys
from mpi4py import MPI
os.environ['lib'] = "/home/chopper/lib"
sys.path.insert(0, os.getenv('lib'))

def batch_run(dirr, num_workers):
    #ASSUMES all files in dirr are config files
    for config_file in os.listdir(dirr):
        print("Starting evo of config file: " + str(config_file))
        configs = init.initialize_master(dirr+"/"+config_file, 0)

        num_workers_configs = int(configs['number_of_workers'])
        if (num_workers != num_workers_configs): print("WARNING in evolve_root.batch_run(): inconsistent # of workers, using command line choice:" + str(num_workers) + ", instead of " + str(num_workers_configs))

        batch_dir = dirr.replace('input','output')
        master.evolve_master(batch_dir, configs, num_workers, cont=False)
    with open(dirr + "/progress.txt", 'w') as out:
        out.write("Done")
    print("Master: Batch run completed.")


def continue_batch(dirr, num_workers):
    #restarts batch run from a checkpoint
    curr_dir, curr_gen, finished_dirs = None, 0, []

    if os.path.isfile(dirr + "/progress.txt"):
        with open (dirr + "/progress.txt") as file:
            lines = file.readlines()
            if (len(lines) > 1):
                curr_dir = lines[0].strip()
                curr_gen = int(lines[-1].strip())

    if os.path.isfile(dirr + "/finished_dirs.txt"):
        with open (dirr + "/finished_dirs.txt") as file:
            finished_dirs = file.readlines()
        for dirr in finished_dirs:
            dirr = dirr.replace('\n','')

    print("evolve_root(): continuing batch run at dir " + str(curr_dir) + " and gen " + str(curr_gen))

    queued_configs = []
    for config_file in os.listdir(dirr):
        new = True
        for finished in finished_dirs:
            if (finished == config_file):
                print("\nevolve_root(): " + str(config_file) + " already finished, skipping.")
                new = False
        if (new == True):
            if (config_file == curr_dir):
                print("\nevolve_root(): continuing curr_dir " + str(config_file))
                configs = init.initialize_master(dirr + "/" + config_file, 0)
                num_workers_configs = int(configs['number_of_workers'])
                if (num_workers != num_workers_configs): print("WARNING in evolve_root.batch_run(): inconsistent # of workers, using command line choice:" + str(num_workers) + ", instead of " + str(num_workers_configs))
                batch_dir = dirr.replace('input', 'output')
                master.evolve_master(batch_dir, configs, num_workers, cont=True)
            else:
                queued_configs.append(config_file)

    for config_file in queued_configs:
        print("Starting evo of config file: " + str(config_file))
        configs = init.initialize_master(dirr+"/"+config_file, 0)
        num_workers_configs = int(configs['number_of_workers'])
        if (num_workers != num_workers_configs): print("WARNING in evolve_root.batch_run(): inconsistent # of workers, using command line choice:" + str(num_workers) + ", instead of " + str(num_workers_configs))
        batch_dir = dirr.replace('input','output')
        master.evolve_master(batch_dir, configs, num_workers, cont=False)

    batch_dir = dirr.replace('input', 'output')
    with open(batch_dir + "/progress.txt", 'w') as out:
        out.write("Done")
    print("Master: Batch run completed.")


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
        continue_batch(dirr, num_workers) #should encompass fresh starts too

    else:
        batch_dir = dirr.replace('input','output')
        import minion

        minion.work(batch_dir, rank)


