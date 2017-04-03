import matplotlib
matplotlib.use('Agg') # This must be done before importing matplotlib.pyplot
import matplotlib.pyplot as plt
import numpy as np
import math
import instances

#TODO: all of it

def leaf_fitness(dirr, Pr, BD_leaf_fitness, title):
    maxBD = len(Pr)
    assert(maxBD == len(Pr[0]))

    Pr_fitness = [0 for i in range(maxBD)]

    for B in range(maxBD):
        for D in range (maxBD):
            if (B+D < maxBD): Pr_fitness[B+D] += Pr[B][D]*BD_leaf_fitness[B][D]*100

    index = [i for i in range(1,maxBD+1)]

    plt.loglog(index,Pr_fitness)
    #plt.yscale('log')

    ax = plt.gca()

    ax.set_ylabel("Cumulative Fitness", fontsize=12)
    ax.set_xlabel("Degree", fontsize=12)
    plt.title("Degree Fitness by BD Probability", fontsize=15)

    if (title != None): plt.savefig(dirr + str(title) + ".png")
    else: plt.savefig(dirr + "Degree_Fitness.png")
    plt.clf()
    plt.cla()
    plt.close()

    return


def unambig_fitness(dirr, Pr):
    maxBD = len(Pr)
    assert(maxBD == len(Pr[0]))

    Pr_fitness = [0 for i in range(maxBD)]

    for B in range(maxBD):
        for D in range (maxBD):
            if (B+D==0): Pr_fitness[B+D] = 0
            elif (B+D < maxBD): Pr_fitness[B+D] += .5*Pr[B][D]**(2*math.log10(B+D))

    index = [i for i in range(1,maxBD+1)]

    plt.loglog(index,Pr_fitness)
    #plt.yscale('log')

    ax = plt.gca()

    ax.set_ylabel("Cumulative Fitness", fontsize=12)
    ax.set_xlabel("Degree", fontsize=12)
    plt.title("Degree Fitness by BD Probability", fontsize=15)

    plt.savefig(dirr + "Degree_Fitness.png")
    plt.clf()
    plt.cla()
    plt.close()

    return

def ETB(dirr, ETB_score, iters):
    return

if __name__ == "__main__":
    dirr_base = "/home/2014/choppe1/Documents/EvoNet/virt_workspace/data/output/"

    Pr = instances.BD_probability(maxBD=20)
    unambig_fitness(dirr_base, Pr)
    print("\nDone making uh plot.\n")
