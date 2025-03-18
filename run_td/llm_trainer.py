import os
import json
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from news_title import NewsCrawler
from module import ExpandIndexRun
from module import Generator_Index
from eval import EvalDayTrade
from module import GeneticAlgorithm

class Trainer:
    def __init__(self, env):
        pass
        self.env = env
        self.price_his = self.get_price_his()
        # self.exp_data = self.llm.get_exp_data