class Result:

    def __init__(self, time_avg_cost, time_avg_cond_drift, obj_function,
                moved_bike_total_count, rebalanced_bike_total_count, total_cycles,
                simulation_hour, distance_moved, demand_supply_gap_total_decrement):
        self.time_avg_cost = time_avg_cost
        self.time_avg_cond_drift = time_avg_cond_drift
        self.obj_function = obj_function
        self.moved_bike_total_count = moved_bike_total_count
        self.rebalanced_bike_total_count = rebalanced_bike_total_count
        self.total_cycles = total_cycles
        self.simulation_hour = simulation_hour
        self.distance_moved = distance_moved
        self.demand_supply_gap_total_decrement = demand_supply_gap_total_decrement
