#TODO: parse pressurize into here?

import math
from operator import attrgetter

def eval_fitness(population, fitness_type):
    #determines fitness of each individual and orders the population by fitness
    if (fitness_type == 15):
        for p in range(len(population)):
            population[p].fitness = population[p].fitness_parts[1]
        population = sorted(population,key=attrgetter('fitness'), reverse=True)
        return

    if (fitness_type % 3 == 0):
        generic_rank(population)

    else:
        for p in range(len(population)):
            if (fitness_type % 3 == 1):
                population[p].fitness = population[p].fitness_parts[0] * population[p].fitness_parts[1]
            else:
                population[p].fitness = math.pow(population[p].fitness_parts[1],population[p].fitness_parts[0])

    population = sorted(population,key=attrgetter('fitness'), reverse=True)
    #reverse since MAX fitness function


def generic_rank(population):

    for p in range(len(population)):
        population[p].fitness = 0

    for i in range(2): #leaf and hub features
        for p in range(len(population)):
            population[p].id = population[p].fitness_parts[i]
        population.sort(key=attrgetter('id'))
        #no reverse, ie MIN features, to MAX fitness consistent with other definitions
        for p in range(len(population)):
            population[p].fitness += p
