from datetime import datetime
from models.settings import Settings

STATUS_START = 'start'
STATUS_REBALANCE = 'rebalance'
STATUS_RIDES = 'rides'
STATUS_NEXT_CYCLE = 'next-cycle'
STATUS_FINISH = 'finish'
STATUS_NONE = None

START_TIME = datetime(year = 2017, month = 9, day = 1, hour = 0)
DEFAULT_SETTINGS = Settings(interval_hour = 2, peak_cost = 1, off_peak_cost = 1, budget_per_cycle = 1000, cost_coef = 0.2)
MOVING_AVERAGE_DAYS = 7

CYCLE_RESULTS_PATH = 'results/cycle_results.csv'
SIMULATION_RESULT_PATH = 'results/simulation_result.csv'
SETTING_PATH = 'results/setting.csv'
SUPPLY_DEMAND_GAP_PATH = 'results/supply_demand_gap.csv'
