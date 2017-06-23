#!/usr/bin/python3
import os,sys
from mpi4py import MPI
os.environ['lib'] = "/home/chopper/lib"
sys.path.insert(0, os.getenv('lib'))
import init, util

def batch_run(dirr, num_workers):
    #OBSOLETE, now handled by batch_root
    #ASSUMES all files in dirr are#  config files
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


def continue_batch(in_dir, num_workers):
    #OBSOLETE, now handled by batch_root
    #restarts batch run from a checkpoint
    curr_dir, curr_gen, finished_dirs = None, 0, []
    out_dir = in_dir.replace('input', 'output')

    if os.path.isfile(out_dir + "/progress.txt"):
        with open (out_dir + "/progress.txt") as file:
            lines = file.readlines()
            print("evolve_root(): progress lines = " + str(lines))
            if (len(lines) > 1):
                curr_dir = lines[0].strip()
                curr_gen = int(lines[-1].strip())  #never used, except for print statement
                print("evolve_root(): found continuation file")


    if os.path.isfile(out_dir + "/finished_dirs.txt"):
        with open (out_dir + "/finished_dirs.txt") as file:
            finished_dirs = file.readlines()
        for dirr in finished_dirs:
            dirr = dirr.replace('\n','')

    print("evolve_root(): continuing batch run at dir " + str(curr_dir) + " and gen " + str(curr_gen) + ".")

    queued_configs = []
    for config_file in os.listdir(in_dir):
        new = True
        for finished in finished_dirs:
            if (finished == config_file):
                print("\nevolve_root(): " + str(config_file) + " already finished, skipping.")
                new = False
        if (new == True):
            configs = init.initialize_master(in_dir+"/"+config_file, 0)
            if (configs['output_directory'] == curr_dir):
                    print("\nevolve_root(): continuing curr_dir " + str(config_file))
                    num_workers_configs = int(configs['number_of_workers'])
                    if (num_workers != num_workers_configs): print("WARNING in evolve_root.batch_run(): inconsistent # of workers, using command line choice:" + str(num_workers) + ", instead of " + str(num_workers_configs))
                    with open(out_dir + "/continue.txt", 'w') as out:
                        out.write(str(curr_gen))  # matters to workers
                    master.evolve_master(out_dir, configs, num_workers, cont=True)
                    os.remove(out_dir + "/continue.txt")

            else: queued_configs.append(configs)

    for configs in queued_configs:
        print("Starting evo of output dir: " + str(configs['output_directory']))
        num_workers_configs = int(configs['number_of_workers'])
        if (num_workers != num_workers_configs): print("WARNING in evolve_root.batch_run(): inconsistent # of workers, using command line choice:" + str(num_workers) + ", instead of " + str(num_workers_configs))
        master.evolve_master(out_dir, configs, num_workers, cont=False)

    with open(out_dir + "/progress.txt", 'w') as out:
        out.write("Done")
    print("Master: Batch run completed.")


def single_run(config_file):
    #OBSOLETE
    #config_file         = util.getCommandLineArgs ()
    configs             = init.initialize_master (config_file, 0)
    master.evolve_master_sequential_debug(configs)
    #master.evolve_master(configs)



if __name__ == "__main__":

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    num_workers = comm.Get_size()  # includes master, so master should also exe 1 worker load
    config_file = sys.argv[1]

    if rank == 0:  # ie is master
        log_text = 'Evolve_root(): in dir ' + str(os.getcwd()) + ', config file = ' + str(config_file) + ', num_workers = ' + str(num_workers)

        import master
        configs = init.initialize_configs(config_file, rank)
        if (configs['num_workers'] != num_workers): print("\nWARNING in evolve_root(): mpi #workers != config #workers!\n")
        util.cluster_print(configs['output_directory'], log_text)
        master.evolve_master(configs)

    else:
        import minion
        configs = init.initialize_configs(config_file, rank)
        minion.work(configs, rank)


