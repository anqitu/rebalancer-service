from geopy.distance import distance
from datetime import datetime
import os

def calculate_distance_between_stations(source, destination):
    return distance((source.coordinates[1],source.coordinates[0]),
                    (destination.coordinates[1], destination.coordinates[0])).km

def current_time():
    return str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

def print_info(info):
    print("{:<6} {}: {}".format('[INFO]', current_time(), info))

def check_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print_info('Make directory: {}'.format(directory))
