from datetime import datetime
from models.settings import Settings

STATUS_START = 'start'
STATUS_REBALANCE = 'rebalance'
STATUS_RIDES = 'rides'
STATUS_NEXT_CYCLE = 'next-cycle'
STATUS_FINISH = 'finish'
STATUS_NONE = None

START_TIME = datetime(year = 2017, month = 8, day = 1, hour = 0)
DEFAULT_SETTINGS = Settings(interval_hour = 6, peak_cost = 10, off_peak_cost = 5, budget_per_cycle = 10000, cost_coef = 0.2)
