import pandas as pd

from utils import *
from constants import *

class PredictionService:

    def __init__(self, setting):

        print_info('Predicting using {}'.format(setting.prediction_mode))
        self.journeys_predict_df = pd.read_csv(PREDICTION_DATA_PATHS[setting.prediction_mode], parse_dates=['Time'])

        self.journeys_predict_df['Hour'] = self.journeys_predict_df['Time'].dt.hour
        # self._make_predictions()

    def get_current_cycle_traffic_prediction_by_time(self, time):

        records = self.journeys_predict_df[(self.journeys_predict_df['Time'] == time)]
        records = {row['Station ID']: {'in': int(row['In']), 'out': int(row['Out'])} for index, row in records[records['Lag'] == 0].iterrows()}
        return records

    def get_next_cycle_traffic_prediction_by_time(self, time):

        records = self.journeys_predict_df[(self.journeys_predict_df['Time'] == time)]
        records = {row['Station ID']: {'in': int(row['In']), 'out': int(row['Out'])} for index, row in records[records['Lag'] == 1].iterrows()}

        return records
