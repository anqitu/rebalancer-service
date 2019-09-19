import pandas as pd
from utils import *
from constants import *

class PredictionService:

    def __init__(self, data_service):

        self.journeys_count_df = data_service.journeys_count_df.copy()
        self._make_predictions()


    def get_predict_flow_by_time(self, time):

        records = self.journeys_count_df[(self.journeys_count_df['Time'] == time)]
        records = {row['Station ID']: {'in': int(row['In']), 'out': int(row['Out'])} for index, row in records.iterrows()}
        return records

    def _make_predictions(self):
        print_info("Start making predictions")
        self.journeys_count_df['Hour'] = self.journeys_count_df['Time'].dt.hour

        prediction_in = self.journeys_count_df.groupby(['Station ID', 'Hour'])[['In']].rolling(window=7).mean()
        prediction_in.index = prediction_in.index.get_level_values(2)
        self.journeys_count_df['In'] = prediction_in.round(0)

        prediction_out = self.journeys_count_df.groupby(['Station ID', 'Hour'])[['Out']].rolling(window=7).mean()
        prediction_out.index = prediction_out.index.get_level_values(2)
        self.journeys_count_df['Out'] = prediction_out.round(0)
        print_info("Finish making predictions")
