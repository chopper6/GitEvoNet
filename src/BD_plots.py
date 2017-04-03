import matplotlib
matplotlib.use('Agg') # This must be done before importing matplotlib.pyplot
import matplotlib.pyplot as plt
import numpy as np
import math

def freq(dirr, freq_orig, iters):

    num_files = len(freq_orig)
    orig_maxBD = len(freq_orig[0])
    maxBD = min(21, len(freq_orig[0]))

    freq = np.zeros((num_files, maxBD, maxBD))
    for i in range(num_files):
        for B in range(maxBD):
            for D in range(maxBD):
                if (B < orig_maxBD and D < orig_maxBD): freq[i][B][D] = freq_orig[i][B][D]

    multiplier = 10000

    for i in range(num_files):
        for B in range(maxBD):
            for D in range(maxBD):
                freq [i][B][D] *= multiplier
                freq[i][B][D] = round(freq[i][B][D])

    zmin = 1      #np.min(freq[np.nonzero(freq)])
    print("BD_plots(): freq min = " + str(zmin))
    zmax = multiplier #np.max(freq[:,:,:])

    for i in range(num_files):

        xydata = freq[i,:maxBD,:maxBD]

        #TODO: log normalize
        plt.matshow(xydata, cmap=plt.get_cmap('plasma'), origin="lower", norm=matplotlib.colors.LogNorm(vmin = zmin, vmax = zmax)) #, vmin=zmin,vmax=zmax)  # , norm=matplotlib.colors.LogNorm())

        ax = plt.gca()
        ax.xaxis.tick_bottom()

        ax.set_ylabel("Benefits", fontsize=12)
        ax.set_xlabel("Damages", fontsize=12)
        ax.xaxis.set_label_position('bottom')
 
        plt.title("Node Frequency", fontsize=15)
        cbar = plt.colorbar(label=str("Percent of nodes"))

        #TODO: add cbar log normz'd labels
        cbar.set_ticks([1, zmax/1000, zmax/100, zmax/10 , zmax])
        cbar.set_ticklabels(["$0$","$10^{-2}$","$10^{-1}$","$10^1$","$10^2$"])
        plt.savefig(dirr + "freq_" + str(iters[i]) + ".png")
        plt.clf()
        plt.cla()
        plt.close()


def probability(dirr, Pr):
    plt.matshow(Pr, cmap=plt.get_cmap('plasma'), origin="lower")

    ax = plt.gca()
    ax.xaxis.tick_bottom()

    ax.set_ylabel("Benefits", fontsize=12)
    ax.set_xlabel("Damages", fontsize=12)
    ax.xaxis.set_label_position('bottom')
    plt.title("Probability of BD Pairs", fontsize=15)
    cbar = plt.colorbar(label=str("probability"))

    # TODO: add cbar labels
    # cbar.set_ticks([0,.1, 1, 10,100 , 1000])
    # maxx =  math.ceil(np.ndarray.max(freq[:,:,:]))
    # cbar.set_ticklabels([0,maxx/1000, maxx/100, maxx/10, maxx])
    # plt.xaxis.set_ticks_position('bottom')
    plt.savefig(dirr + "probability.png")
    plt.clf()
    plt.cla()
    plt.close()

def leaf_fitness(dirr, leaf_fitness):
    plt.matshow(leaf_fitness, cmap=plt.get_cmap('plasma'), origin="lower")

    ax = plt.gca()
    ax.xaxis.tick_bottom()

    ax.set_ylabel("Benefits", fontsize=12)
    ax.set_xlabel("Damages", fontsize=12)
    ax.xaxis.set_label_position('bottom')

    plt.title("Leaf Fitness of BD Pairs", fontsize=15)
    cbar = plt.colorbar(label=str("probability"))

    # TODO: add cbar labels
    # cbar.set_ticks([0,.1, 1, 10,100 , 1000])
    # maxx =  math.ceil(np.ndarray.max(freq[:,:,:]))
    # cbar.set_ticklabels([0,maxx/1000, maxx/100, maxx/10, maxx])
    # plt.xaxis.set_ticks_position('bottom')
    plt.savefig(dirr + "leaf_fitness.png")
    plt.clf()
    plt.cla()
    plt.close()


def Pr_leaf_fitness(dirr, Pr, leaf_fitness):
    size = len(Pr)
    Pr_fitness = [[Pr[i][j] * leaf_fitness[i][j] for i in range(size)] for j in range(size)]

    plt.matshow(Pr_fitness, cmap=plt.get_cmap('plasma'), origin="lower")

    ax = plt.gca()
    ax.xaxis.tick_bottom()
    ax.set_ylabel("Benefits", fontsize=12)
    ax.set_xlabel("Damages", fontsize=12)
    ax.xaxis.set_label_position('bottom')

    plt.title("Leaf Fitness * Probability of BD Pairs", fontsize=15)
    cbar = plt.colorbar(label=str("probability"))

    # TODO: add cbar labels
    # cbar.set_ticks([0,.1, 1, 10,100 , 1000])
    # maxx =  math.ceil(np.ndarray.max(freq[:,:,:]))
    # cbar.set_ticklabels([0,maxx/1000, maxx/100, maxx/10, maxx])
    # plt.xaxis.set_ticks_position('bottom')
    plt.savefig(dirr + "probability_leaf_fitness.png")
    plt.clf()
    plt.cla()
    plt.close()

def ETB(dirr, ETB_score, iters):
    num_files = len(ETB_score)
    #multiplier = 1000
    zmin = 0
    zmax = np.max(ETB_score[:,:,:])

    for i in range(num_files):
        xydata = ETB_score[i]

        plt.matshow(xydata, cmap=plt.get_cmap('plasma'), origin="lower", vmin=zmin,vmax=zmax)

        ax = plt.gca()
        ax.xaxis.tick_bottom()

        ax.set_ylabel("Benefits", fontsize=12)
        ax.set_xlabel("Damages", fontsize=12)
        ax.xaxis.set_label_position('bottom')

        plt.title("Hub Fitness", fontsize=15)
        cbar = plt.colorbar(label=str("Average Contribution"))
        cbar.ax.tick_params(labelsize=10)

        plt.savefig(dirr + "ETB_" + str(iters[i]) + ".png")
        plt.clf()
        plt.cla()
        plt.close()


