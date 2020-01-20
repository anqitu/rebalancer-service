from datetime import datetime
from models.settings import Settings
import os
from utils import *

STATUS_START = 'start'
STATUS_REBALANCE = 'rebalance'
STATUS_RIDES = 'rides'
STATUS_NEXT_CYCLE = 'next-cycle'
STATUS_FINISH = 'finish'
STATUS_NONE = None

PREDICTION_MODE_7DMA = 'Past 7 Days Moving Average'
PREDICTION_MODE_LSTM = 'LSTM'
PREDICTION_MODE_GRU = 'GRU'
PREDICTION_MODE_BI_LSTM = 'Bidirectional LSTM'

START_TIME = datetime(year = 2017, month = 9, day = 10, hour = 0)
DEFAULT_SETTINGS = Settings(interval_hour = 2, peak_cost = 1, off_peak_cost = 1,
                            budget_per_cycle = 1500, cost_coef = 0.2,
                            prediction_mode = PREDICTION_MODE_7DMA)
MOVING_AVERAGE_DAYS = 7

RESULTS_PATH = 'results'
check_dir(RESULTS_PATH)
CYCLE_RESULTS_PATH = os.path.join(RESULTS_PATH, 'cycle_results.csv')
SIMULATION_RESULT_PATH = os.path.join(RESULTS_PATH, 'simulation_result.csv')
SETTING_PATH = os.path.join(RESULTS_PATH, 'setting.csv')
SUPPLY_DEMAND_GAP_PATH = os.path.join(RESULTS_PATH, 'supply_demand_gap.csv')
JOURNEYS_DATA_PATH = 'data/london_journeys_count_with_2h_interval.csv'
STATIONS_DATA_PATH = 'data/london_stations.json'
PREDICTION_DATA_PATHS = {
    PREDICTION_MODE_7DMA: 'data/london_journeys_predict_with_2h_interval_7DMA.csv',
    PREDICTION_MODE_LSTM: 'data/london_journeys_predict_with_2h_interval_LSTM.csv',
    PREDICTION_MODE_GRU: 'data/london_journeys_predict_with_2h_interval_GRU.csv',
    PREDICTION_MODE_BI_LSTM: 'data/london_journeys_predict_with_2h_interval_Bidirectional LSTM.csv'
}
