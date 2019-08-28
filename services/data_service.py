import pandas as pd

data_path = 'data/london_stations_in_out_with_6h_interval.json'

class DataService:

    def __init__(self):
        self.journeys_count_df = pd.read_csv('data/london_journeys_count_with_6h_interval.csv')
        # journeys_count_df = pd.read_csv('../data/london_journeys_count_with_6h_interval.csv')
        self.journeys_count_df['Time'] = pd.to_datetime(self.journeys_count_df['Time'],infer_datetime_format=True)

        # journeys_count_df.head()

    def get_station_data(self, station_id, time):
        # station_id = 302
        # time = pd.Timestamp(year=2017, month=8, day=1, hour=0)
        record = self.journeys_count_df[(self.journeys_count_df['Station ID'] == station_id) & (self.journeys_count_df['Time'] == time)]
        return {'out': int(record['Out'].values[0]), 'in': int(record['In'].values[0])}
