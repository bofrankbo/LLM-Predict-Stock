import os
import json
import random
from api.eval import eval

# 儲存-----------------------------------------
# 儲存狀態
def save_state(filename, state, message):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        json.dump(state, f)

# 載入狀態
def load_state(filename):
    try:
        with open(filename, 'r') as f:
            content = f.read().strip()
            if not content:
                return None
            return json.loads(content)
    except FileNotFoundError:
        return None

# 儲存每一代的結果
def save_generation_results(filename, generation, best_individual, best_fitness):
    result = {
        "generation": generation,
        "best_individual": best_individual,
        "best_fitness": best_fitness
    }
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'a') as f:
        f.write(json.dumps(result) + '\n')

# 遺傳演算法-----------------------------------------
# 初始群體生成
def generate_population(size, num_elements):
    population = []
    for _ in range(size):
        individual = [random.randint(0, 1) for _ in range(num_elements)]
        population.append(individual)
    return population

# 適應度函數
def fitness(individual, env, train_datarange, mode, state_file, individual_score, current_generation):
    result = eval(individual, train_datarange, env)
    if mode == 0:
        score = result['accuracy']
    else:
        score = result['ev']

    individual_score[str(individual)] = score

    state = load_state(state_file)
    if state:
        current_pop = state['population']
    save_state(state_file, {'generation': current_generation, 'population': current_pop, 'individual_score': individual_score}, "fitness")

    return score

# 選擇
def selection(population, env, train_datarange, mode, state_file, individual_score, current_generation):
    population.sort(key=lambda ind: fitness(ind, env, train_datarange, mode, state_file, individual_score, current_generation), reverse=True)
    return population[:int(len(population)/2)]

# 交叉
def crossover(parent1, parent2, crossover_rate=0.7):
    if random.random() <= crossover_rate:
        idx = random.randint(1, len(parent1) - 1)
        child1 = parent1[:idx] + parent2[idx:]
        child2 = parent2[:idx] + parent1[idx:]
    else:
        child1, child2 = parent1, parent2
    return child1, child2

# 變異
def mutate(individual, mutation_rate=0.005):
    for i in range(len(individual)):
        if random.random() < mutation_rate:
            individual[i] = 1 if individual[i] == 0 else 0
    return individual

# 主程式-----------------------------------------
def genetic_algorithm(factors, population_size=20, generations=50, state_file='', results_file='', env=None, mode=0, datarange=None):
    individual_score = {}
    current_generation = 0

    state = load_state(state_file)
    if state:
        current_population = state['population']
        start_generation = state['generation']
        individual_score = state['individual_score']
        if len(current_population) == 0:
            current_population = generate_population(population_size, len(factors))
        if start_generation >= generations:
            return max(current_population, key=lambda ind: fitness(ind, env, datarange, mode, state_file, individual_score, start_generation))
    else:
        current_population = generate_population(population_size, len(factors))
        start_generation = 0

    save_state(state_file, {'generation': start_generation, 'population': current_population, 'individual_score': individual_score}, "init")

    for current_generation in range(start_generation, generations):
        print(f"Generation {current_generation+1}")
        selected = selection(current_population, env, datarange, mode, state_file, individual_score, current_generation)
        children = []
        while len(children) < population_size:
            parent1, parent2 = random.sample(selected, 2)
            child1, child2 = crossover(parent1, parent2)
            children.append(mutate(child1, 0.005))
            children.append(mutate(child2, 0.005))
        current_population = children
        best_individual = max(current_population, key=lambda ind: fitness(ind, env, datarange, mode, state_file, individual_score, current_generation))
        best_fitness = fitness(best_individual, env, datarange, mode, state_file, individual_score, current_generation)
        print(f"Best fitness = {best_fitness}")
        print(f"Best individual: {best_individual}")

        save_state(state_file, {'generation': current_generation+1, 'population': current_population, 'individual_score': individual_score}, "every generation")
        save_generation_results(results_file, current_generation + 1, best_individual, best_fitness)
        print()

    return best_individual