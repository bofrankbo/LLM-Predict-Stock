import os
import json
import random
from .GA import GeneticAlgorithm

class GA_UsablePlus24(GeneticAlgorithm):
    def generate_population(self):
        population = []
        for _ in range(self.population_size):
            # 前8個因子固定為1，其他隨機
            # individual = [1, 1, 1, 1, 1, 1, 1, 1] + [random.randint(0, 1) for _ in range(self.population_length - 8)]
            
            # 32個因子，前8個隨機，第二個8個設成2進位的60，第三個8個設成2進位的60，最後8個設成2進位的128
            individual = [random.randint(0, 1) for _ in range(8)] + [int(i) for i in list(format(60, '08b'))] + [int(i) for i in list(format(60, '08b'))] + [int(i) for i in list(format(128, '08b'))]
            
            # # 一般 individual
            # individual = [random.randint(0, 1) for _ in range(self.population_length)]
            population.append(individual)
        return population
    