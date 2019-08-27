import uuid

from models.station import Station

class Trip:

    def __init__(self, source, destination):
        self.id = uuid.uuid4()
        self.source = source
        self.destination = destination
        self.distance = self.__calculate_distance()

    def set_rebalanced_bike_count(self, rebalanced_bike_count):
        self.rebalanced_bike_count = rebalanced_bike_count
        self.rebalance_cost = self.__calculate_cost()

    def __calculate_distance(self):
        return 20

    def __calculate_cost(self):
        return 100
