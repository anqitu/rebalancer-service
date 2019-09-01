from models.settings import Settings
from models.cycle import Cycle
from constants import *

import time;

class Simulation:

    def __init__(self, setting):
        self.setting = setting
        self.start_time = time.time()
        self.cycles = []

    def set_result(self, result):
        self.result = result

    def add_cycle(self, cycle):
        self.cycles.append(cycle)
