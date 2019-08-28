class Result:

    def __init__(self, time_avg_cost, time_avg_cond_drift, obj_function,
                moved_bike_total_count, rebalanced_bike_total_count, cycle_count,
                simulation_hour):
        self.time_avg_cost = time_avg_cost
        self.time_avg_cond_drift = time_avg_cond_drift
        self.obj_function = obj_function
        self.moved_bike_total_count = moved_bike_total_count
        self.rebalanced_bike_total_count = rebalanced_bike_total_count
        self.cycle_count = cycle_count
        self.simulation_hour = simulation_hour
