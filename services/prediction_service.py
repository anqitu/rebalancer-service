import pandas as pd

from utils import *
from constants import *

class PredictionService:

    def __init__(self, setting):

        if setting.prediction_mode == PREDICTION_MODE_MOVING_AVG:
            self.journeys_predict_df = pd.read_csv(JOURNEYS_PREDICTION_7DMA, parse_dates=['Time'])
        elif setting.prediction_mode == PREDICTION_MODE_LSTM:
            self.journeys_predict_df = pd.read_csv(JOURNEYS_PREDICTION_LSTM, parse_dates=['Time'])

        self.journeys_predict_df['Hour'] = self.journeys_predict_df['Time'].dt.hour
        # self._make_predictions()

    def get_predict_flow_by_time(self, time):

        records = self.journeys_predict_df[(self.journeys_predict_df['Time'] == time)]
        records = {row['Station ID']: {'in': int(row['In']), 'out': int(row['Out'])} for index, row in records.iterrows()}
        return records

    # def _make_predictions(self):
    #     print_info("Start making predictions")
    #
    #     prediction_in = self.journeys_predict_df.groupby(['Station ID', 'Hour'])[['In']].rolling(window=7).mean()
    #     prediction_in.index = prediction_in.index.get_level_values(2)
    #     self.journeys_predict_df['In'] = prediction_in.round(0)
    #
    #     prediction_out = self.journeys_predict_df.groupby(['Station ID', 'Hour'])[['Out']].rolling(window=7).mean()
    #     prediction_out.index = prediction_out.index.get_level_values(2)
    #     self.journeys_predict_df['Out'] = prediction_out.round(0)
    #     print_info("Finish making predictions")
