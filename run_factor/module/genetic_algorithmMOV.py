import os
import json
import random
from .genetic_algorithm import GeneticAlgorithm

class GeneticAlgorithmMOV(GeneticAlgorithm):
    def __init__(self, env, df_price_his, datarange, eval_func, pop_size=20, generations=50, mode=0, pop_len=20):
        self.env = env
        self.path_out =  f"{env['path_folder']}/{env['start_date']}_{env['end_date']}/{env['stock_id']}"
        self.training_path = f"out_stock/Training_result/{env['path_folder']}/{env['MOV']}/{env['run_count']}/{env['start_date']}_{env['end_date']}/{env['stock_id']}"

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