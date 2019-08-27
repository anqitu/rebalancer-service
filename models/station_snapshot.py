from models.station import Station

class StationSnapshot:

    def __init__(self, station):
        self.station = station

    def set_available_bike_count_before_rebalance(self, available_bike_count_before_rebalance):
        self.available_bike_count_before_rebalance = available_bike_count_before_rebalance

    def set_expected_incoming_bike_count(self, expected_incoming_bike_count):
        self.expected_incoming_bike_count = expected_incoming_bike_count

    def set_expected_outgoing_bike_count(self, expected_outgoing_bike_count):
        self.expected_outgoing_bike_count = expected_outgoing_bike_count

    def set_target_bike_count(self, target_bike_count):
        self.target_bike_count = target_bike_count

    def set_rebalanced_bike_count(self, rebalanced_bike_count):
        self.rebalanced_bike_count = rebalanced_bike_count

    def set_available_bike_count_after_rebalance(self, available_bike_count_after_rebalance):
        self.available_bike_count_after_rebalance = available_bike_count_after_rebalance

    def set_actual_incoming_bike_count(self, actual_incoming_bike_count):
        self.actual_incoming_bike_count = actual_incoming_bike_count

    def set_actual_outgoing_bike_count(self, actual_outgoing_bike_count):
        self.actual_outgoing_bike_count = actual_outgoing_bike_count

    def set_available_bike_count_after_rides(self, available_bike_count_after_rides):
        self.available_bike_count_after_rides = available_bike_count_after_rides
