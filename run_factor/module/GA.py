import os
import json
import random

class GeneticAlgorithm:
    def __init__(self, env, df_price_his, datarange, eval_func, pop_size=20, generations=50, mode=0, pop_len=20):
        self.env = env
        self.training_path = self.env['training_path']

        if mode == 0:
            out_folder = f"{self.training_path}/ac"
        elif mode == 1:
            out_folder = f"{self.training_path}/ev"
        
        self.state_file = out_folder + '/state.json'
        self.results_file = out_folder + '/generation_results.json'
        self.datarange = datarange
        self.df_price_his = df_price_his
        self.eval_func = eval_func
        self.population_size = pop_size
        self.population_length = pop_len
        self.generations = generations
        self.mode = mode
        self.individual_score = {}
        self.current_generation = 0
        self.current_population = self.load_state()

    def save_state(self, state):
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=4)

    def load_state(self):
        try:
            with open(self.state_file, 'r') as f:
                content = f.read().strip()
                state = json.loads(content)
                if not state['population']:
                    return self.generate_population()
                
                self.current_generation = state['generation']
                self.individual_score = state['individual_score']
                self.current_population = state['population']
                return self.current_population
        except FileNotFoundError:
            return self.generate_population()

    def save_generation_results(self, generation, best_individual, best_fitness):
        result = {
            "generation": generation,
            "best_individual": best_individual,
            "best_fitness": best_fitness
        }
        os.makedirs(os.path.dirname(self.results_file), exist_ok=True)
        with open(self.results_file, 'a') as f:
            f.write(json.dumps(result) + '\n')

    def generate_population(self):
        population = []
        for _ in range(self.population_size):
            # 前8個因子固定為1，其他隨機
            # individual = [1, 1, 1, 1, 1, 1, 1, 1] + [random.randint(0, 1) for _ in range(self.population_length - 8)]
            
            # 32個因子，前8個隨機，第二個8個設成2進位的60，第三個8個設成2進位的60，最後8個設成2進位的128
            # individual = [random.randint(0, 1) for _ in range(8)] + [int(i) for i in list(format(60, '08b'))] + [int(i) for i in list(format(60, '08b'))] + [int(i) for i in list(format(128, '08b'))]
            
            # 一般 individual
            individual = [random.randint(0, 1) for _ in range(self.population_length)]
            
            population.append(individual)
        return population

    def fitness(self, individual):
        state = self.load_state()
        if state:
            if self.individual_score.get(str(individual)):
                return self.individual_score[str(individual)]
        
        new_indv = individual.copy()
        result = self.eval_func(self.datarange, new_indv)
        score = result['accuracy'] if self.mode == 0 else result['ev']
        self.individual_score[str(individual)] = score

        self.save_state({'generation': self.current_generation, 'population': self.current_population, 'individual_score': self.individual_score})
        return score

    def selection(self, population):
        population.sort(key=lambda ind: self.fitness(ind), reverse=True)
        return population[:int(len(population)/2)]

    def crossover(self, parent1, parent2, crossover_rate=0.7):
        if random.random() <= crossover_rate:
            idx = random.randint(1, len(parent1) - 1)
            child1 = parent1[:idx] + parent2[idx:]
            child2 = parent2[:idx] + parent1[idx:]
        else:
            child1, child2 = parent1, parent2
        return child1, child2

    def mutate(self, individual, mutation_rate=0.005):
        for i in range(len(individual)):
            if random.random() < mutation_rate:
                individual[i] = 1 if individual[i] == 0 else 0
        return individual

    def run(self):
        if self.current_generation >= self.generations:
            with open(self.results_file, 'r') as f:
                for line in f:
                    result = json.loads(line)
                    if result['generation'] == self.generations:
                        return result['best_individual']
            return max(self.current_population, key=lambda ind: self.fitness(ind))

        self.save_state({'generation': self.current_generation, 'population': self.current_population, 'individual_score': self.individual_score})

        print(f"Start Running Genetic Algorithm")
        for self.current_generation in range(self.current_generation, self.generations):
            selected = self.selection(self.current_population)
            children = []
            # print(selected)
            while len(children) < self.population_size:
                parent1, parent2 = random.sample(selected, 2)
                child1, child2 = self.crossover(parent1, parent2)
                children.append(self.mutate(child1))
                children.append(self.mutate(child2))
            self.current_population = children
            best_individual = max(self.current_population, key=lambda ind: self.fitness(ind))
            best_fitness = self.fitness(best_individual)

            self.save_state({'generation': self.current_generation + 1, 'population': self.current_population, 'individual_score': self.individual_score})
            self.save_generation_results(self.current_generation + 1, best_individual, best_fitness)

        # 從 state.json 中取得最佳個體
        
        best_individual = max(self.individual_score, key=self.individual_score.get)
        # best_individual = "[0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1]"
        # switch to list, element to int
        best_fitness = self.individual_score[best_individual]
        list_best_individual = best_individual.replace("[", "").replace("]", "").replace(" ", "").split(",")
        list_best_individual = [int(i) for i in list_best_individual]
        # print(list_best_individual)
        
        return list_best_individual