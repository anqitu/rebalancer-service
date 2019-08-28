import uuid
from models.station import Station
from utils import *

class RebalanceSchedule:

    def __init__(self, source, destination, rebalanced_bike_count, rebalance_cost):
        self.id = uuid.uuid4()
        self.source = source
        self.destination = destination
        self.distance = calculate_distance_between_stations(source, destination)
        self.rebalanced_bike_count = rebalanced_bike_count
        self.rebalance_cost = rebalance_cost
