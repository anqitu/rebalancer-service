class Setting:

    def __init__(self, interval_hour, peak_cost, off_peak_cost, budget_per_cycle, cost_coef):
        self.interval_hour = interval_hour
        self.peak_cost = peak_cost
        self.off_peak_cost = off_peak_cost
        self.budget_per_cycle = budget_per_cycle
