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
    'rebalanced_bike_count': 'Rebalanced Bikes',
    'cumulative_rebalanced_bike_count': 'Cumulative Rebalanced Bikes',
    'rebalance_cost': 'Rebalanced Cost',
    'cumulative_rebalance_cost': 'Cumulative Rebalance Cost',
    'time_avg_rebalance_cost': 'Time Average Rebalance Cost',
    'trips': 'Trips',
    'distance_moved': 'Distance Moved',
    'cumulative_distance_moved': 'Cumulative Distance Moved',
    'supply_demand_gap_before_rebalance': 'Supply Demand Gap Before Rebalance',
    'supply_demand_gap_after_rebalance': 'Supply Demand Gap After Rebalance',
    'lyapunov': 'Lyapunov',
    'lyapunov_drift': 'Lyapunov Drift',
    'cumulative_drift': 'Cumulative Lyapunov',
    'time_avg_cond_drift': 'Time Average Conditional Drift'}

RESULTS_MAPPER = {'cycle_count': 'Cycle Count',
    'simulation_hour': 'Simulation Hours',
    'moved_bike_total_count': 'Moved Bike Total Count',
    'rebalanced_bike_total_count': 'Rebalanced Bike Total Count',
    'time_avg_cost': 'Time Average Cost',
    'time_avg_cond_drift': 'Time Average Conditional Drift',
    'obj_function': 'Objective Function'}
