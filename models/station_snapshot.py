from models.station import Station

class StationSnapshot:

    def __init__(self, station = None, previous_station_snapshot = None):
        if station:
            self.station = station
        else:
            self.station = previous_station_snapshot.station
            self.available_bike_count_before_rebalance = previous_station_snapshot.available_bike_count_after_rides
            self.current_bike_count = self.available_bike_count_before_rebalance
            self.available_bike_count_after_rebalance = self.available_bike_count_before_rebalance

        self.rebalanced_bike_count = 0

    def set_initial_available_bike_count(self, ratio):
        self.available_bike_count_before_rebalance = int(self.station.capacity * ratio)
        self.current_bike_count = self.available_bike_count_before_rebalance
        self.available_bike_count_after_rebalance = self.available_bike_count_before_rebalance

    def set_expected_incoming_bike_count(self, expected_incoming_bike_count):
        self.expected_incoming_bike_count = expected_incoming_bike_count

    def set_expected_outgoing_bike_count(self, expected_outgoing_bike_count):
        self.expected_outgoing_bike_count = expected_outgoing_bike_count

    def set_target_bike_count(self, target_bike_count):
        self.target_bike_count = target_bike_count
        self.demand_supply_gap_before_rebalance =  self.target_bike_count - self.available_bike_count_before_rebalance

    def set_next_cycle_expected_incoming_bike_count(self, next_cycle_expected_incoming_bike_count):
        self.next_cycle_expected_incoming_bike_count = next_cycle_expected_incoming_bike_count

    def set_next_cycle_expected_outgoing_bike_count(self, next_cycle_expected_outgoing_bike_count):
        self.next_cycle_expected_outgoing_bike_count = next_cycle_expected_outgoing_bike_count

    def set_next_cycle_target_bike_count(self, next_cycle_target_bike_count):
        self.next_cycle_target_bike_count = next_cycle_target_bike_count

    def set_target_rebalance_bike_count(self, target_rebalance_bike_count):
        self.target_rebalance_bike_count = target_rebalance_bike_count

    def update_rebalanced_bike_count(self, rebalanced_bike_count_change):
        self.rebalanced_bike_count += rebalanced_bike_count_change
        self.available_bike_count_after_rebalance = self.available_bike_count_before_rebalance + self.rebalanced_bike_count
        self.current_bike_count = self.available_bike_count_after_rebalance

    def set_actual_incoming_bike_count(self, actual_incoming_bike_count):
        self.actual_incoming_bike_count = actual_incoming_bike_count

    def set_actual_outgoing_bike_count(self, actual_outgoing_bike_count):
        self.actual_outgoing_bike_count = actual_outgoing_bike_count

    def calculate_demand_supply_gap_after_rebalance(self):
        self.demand_supply_gap_after_rebalance = self.target_bike_count - self.available_bike_count_after_rebalance

    def calculate_available_bike_count_after_rides(self):
        self.available_bike_count_after_rides = max(self.available_bike_count_after_rebalance \
                                                + self.actual_incoming_bike_count \
                                                - self.actual_outgoing_bike_count, 0)
        self.current_bike_count = self.available_bike_count_after_rides
