from models.station import Station

class StationSnapshot:

    def __init__(self, station):
        self.station = station

    def set_available_bike_count_before_rebalance(self, available_bike_count_before_rebalance):
        self.available_bike_count_before_rebalance = available_bike_count_before_rebalance

    def set_incoming_bike_count(self, incoming_bike_count):
        self.incoming_bike_count = incoming_bike_count

    def set_outgoing_bike_count(self, outgoing_bike_count):
        self.outgoing_bike_count = outgoing_bike_count

    def set_target_bike_count(self, target_bike_count):
        self.target_bike_count = target_bike_count

    def set_rebalanced_bike_count(self, rebalanced_bike_count):
        self.rebalanced_bike_count = rebalanced_bike_count

    def set_available_bike_count_after_rebalance(self, available_bike_count_after_rebalance):
        self.available_bike_count_after_rebalance = available_bike_count_after_rebalance
