import matplotlib
matplotlib.use('Agg') # This must be done before importing matplotlib.pyplot
import matplotlib.pyplot as plt
import numpy as np


def freq(dirr, freq, iters):

    num_files = len(freq)
    multiplier = 1000
    zmin = 0 #np.min(freq[:,:,:])
    zmax = multiplier
    np.multiply(freq, multiplier)
    np.round(freq)

    for i in range(num_files):
        xydata = freq[i]

        #TODO: log normalize
        plt.matshow(xydata, cmap=plt.get_cmap('plasma'), origin="lower", vmin=zmin,vmax=zmax)  # , norm=matplotlib.colors.LogNorm())

        plt.ylabel("Benefits", fontsize=15)
        plt.xlabel("Damages", fontsize=15)
        plt.title("Frequency of BD Pairs", fontsize=20)
        cbar = plt.colorbar(label=str("frequency"))

        #TODO: add cbar log normz'd labels
        # cbar.set_ticks([0,.1, 1, 10,100 , 1000])
        # maxx =  math.ceil(np.ndarray.max(freq[:,:,:]))
        # cbar.set_ticklabels([0,maxx/1000, maxx/100, maxx/10, maxx])
        # plt.xaxis.set_ticks_position('bottom')
        plt.savefig(dirr + "freq_ + " + str(iters[i]) + ".png")
        plt.clf()
        plt.cla()
        plt.close()


def probability(dirr, Pr):
    plt.matshow(Pr, cmap=plt.get_cmap('plasma'), origin="lower")

    plt.ylabel("Benefits", fontsize=15)
    plt.xlabel("Damages", fontsize=15)
    plt.title("Probability of BD Pairs", fontsize=20)
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

    plt.ylabel("Benefits", fontsize=15)
    plt.xlabel("Damages", fontsize=15)
    plt.title("Leaf Fitness of BD Pairs", fontsize=20)
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

    plt.ylabel("Benefits", fontsize=15)
    plt.xlabel("Damages", fontsize=15)
    plt.title("Leaf Fitness * Probability of BD Pairs", fontsize=20)
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
    multiplier = 1000
    zmin = 0
    zmax = np.max[ETB_score[:,:,:]]

    for i in range(num_files):
        xydata = ETB_score[i]

        plt.matshow(xydata, cmap=plt.get_cmap('plasma'), origin="lower", vmin=zmin,vmax=zmax)

        plt.ylabel("Benefits", fontsize=15)
        plt.xlabel("Damages", fontsize=15)
        plt.title("ETB of BD Pairs", fontsize=20)
        cbar = plt.colorbar(label=str("ETB"))

        #TODO: add cbar log normz'd labels
        # cbar.set_ticks([0,.1, 1, 10,100 , 1000])
        # maxx =  math.ceil(np.ndarray.max(freq[:,:,:]))
        # cbar.set_ticklabels([0,maxx/1000, maxx/100, maxx/10, maxx])
        # plt.xaxis.set_ticks_position('bottom')
        plt.savefig(dirr + "ETB_ + " + str(iters[i]) + ".png")
        plt.clf()
        plt.cla()
        plt.close()