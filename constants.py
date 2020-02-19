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
PREDICTION_MODE_BI_LSTM = 'Bi-LSTM'
PREDICTION_MODE_ACTUAL = 'ACTUAL'

START_TIME = datetime(year = 2018, month = 10, day = 1, hour = 0)
DEFAULT_SETTINGS = Settings(interval_hour = 2, peak_cost = 2, off_peak_cost = 1,
                            budget_per_cycle = 1500, cost_coef = 0.2,
                            prediction_mode = PREDICTION_MODE_7DMA)
MOVING_AVERAGE_DAYS = 7

RESULTS_PATH = 'results'
check_dir(RESULTS_PATH)
DATA_PATH = 'data'
JOURNEYS_DATA_PATH = os.path.join(DATA_PATH, 'london_journeys_count_with_2h_interval.csv')
STATIONS_DATA_PATH = os.path.join(DATA_PATH, 'london_stations.json')
PREDICTION_DATA_PATHS = {
    PREDICTION_MODE_7DMA: os.path.join(DATA_PATH, 'london_journeys_predict_with_2h_interval_7DMA.csv'),
    PREDICTION_MODE_LSTM: os.path.join(DATA_PATH, 'london_journeys_predict_with_2h_interval_LSTM.csv'),
    PREDICTION_MODE_GRU: os.path.join(DATA_PATH, 'london_journeys_predict_with_2h_interval_GRU.csv'),
    PREDICTION_MODE_BI_LSTM: os.path.join(DATA_PATH, 'london_journeys_predict_with_2h_interval_Bi-LSTM.csv'),
    PREDICTION_MODE_ACTUAL: os.path.join(DATA_PATH, 'london_journeys_predict_with_2h_interval_actual.csv'),
}

SETTINGS_UI_MAPPER = {'peak_cost': 'peakCost',
                    'off_peak_cost': 'offPeakCost',
                    'budget_per_cycle': 'budgetPerCycle',
                    'cost_coef': 'costCoef',
                    'prediction_mode': 'predictionMode'}

SETTINGS_CSV_MAPPER = {'peak_cost': 'Peak Cost',
                    'off_peak_cost': 'Off-Peak Cost',
                    'budget_per_cycle': 'Budget Per Cycle',
                    'cost_coef': 'Cost Coef',
                    'prediction_mode': 'Prediction Mode'}

STATISTICS_MAPPER = {'count': 'Cycle Count',
    'moved_bike_count': 'Moved Bikes',
    'cumulative_moved_bike_count': 'Cumulative Moved Bikes',
    'trips_scheduled': 'Trips Scheduled',
    'distance_moved': 'Distance Moved',
    'cumulative_distance_moved': 'Cumulative Distance Moved',
    'rebalanced_bike_count': 'Rebalanced Bikes',
    'cumulative_rebalanced_bike_count': 'Cumulative Rebalanced Bikes',
    'rebalance_cost': 'Rebalanced Cost',
    'cumulative_rebalance_cost': 'Cumulative Rebalance Cost',
    'time_avg_rebalance_cost': 'Time Average Rebalance Cost',
    'lyapunov': 'Lyapunov',
    'lyapunov_drift': 'Lyapunov Drift',
    'cumulative_drift': 'Cumulative Lyapunov',
    'time_avg_cond_drift': 'Time Average Conditional Drift',
    'demand_supply_gap_before_rebalance': 'Demand Supply Gap Before Rebalance',
    'demand_supply_gap_after_rebalance': 'Demand Supply Gap After Rebalance',
    'demand_supply_gap_decrement': 'Demand Supply Gap Decrement',
    'cumulative_demand_supply_gap_decrement': 'Cumulative Demand Supply Gap Decrement',
    }

RESULTS_MAPPER = {'total_cycles': 'Cycles',
    'simulation_hour': 'Hours',
    'moved_bike_total_count': 'Moved Bikes',
    'rebalanced_bike_total_count': 'Rebalanced Bikes',
    'time_avg_cost': 'Time Average Cost',
    'time_avg_cond_drift': 'Time Average Conditional Drift',
    'obj_function': 'Objective Function',
    'demand_supply_gap_total_decrement': 'Demand Supply Gap Decrement',
    }
