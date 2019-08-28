import pandas as pd

data_path = 'data/london_journeys_count_with_6h_interval.csv'

class PredictionService:

    def __init__(self):
        self.journeys_count_df = pd.read_csv(data_path)
        self.journeys_count_df['Time'] = pd.to_datetime(self.journeys_count_df['Time'],infer_datetime_format=True)

    def get_station_data(self, station_id, time):

        record = self.journeys_count_df[(self.journeys_count_df['Station ID'] == station_id) & (self.journeys_count_df['Time'] == time)]
        return {'out': int(record['Out'].values[0]), 'in': int(record['In'].values[0])}
