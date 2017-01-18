#!/usr/bin/python3
import os,sys
os.environ['lib'] = "/home/2014/choppe1/Documents/EvoNet/virt_workspace/lib"
sys.path.insert(0, os.getenv('lib'))
import util, init, solver, reducer, master


# TODO: check class scope, is it suffic to just have in master?
# maybe rename to reduce confusion
class Net:
    def __init__(self, net, id):
        self.fitness = 0    #aim to max
        self.fitness_parts = [0]*2   #leaf-fitness, hub-fitness
        self.net = net.copy()
        self.id = id  #irrelv i think

    def copy(self):
        copy = Net(self.net, self.id)
        copy.fitness = self.fitness
        copy.fitness_parts[0] = self.fitness_parts[0]
        copy.fitness_parts[1] = self.fitness_parts[1]
        assert (copy != self)
        return copy



if __name__ == "__main__":

    config_file         = util.getCommandLineArgs ()
    M, configs          = init.initialize_master (config_file, 0)

    #master.evolve_master_sequential_debug(configs)
    master.evolve_master(configs)
