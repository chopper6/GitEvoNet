import matplotlib
matplotlib.use('Agg') # This must be done before importing matplotlib.pyplot
import matplotlib.pyplot as plt
import numpy as np

#TODO: all of it

def leaf_fitness(dirr, Pr, BD_leaf_fitness):
    maxBD = len(Pr)
    assert(maxBD == len(Pr[0]))

    Pr_fitness = [0 for i in range(maxBD)]

    for B in range(maxBD):
        for D in range (maxBD):
            if (B+D < maxBD): Pr_fitness[B+D] += Pr[B][D]*BD_leaf_fitness[B][D]

    index = [i for i in range(maxBD)]

    plt.bar(index, Pr_fitness)

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