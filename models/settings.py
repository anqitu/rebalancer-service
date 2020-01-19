class Settings:

    def __init__(self, interval_hour, peak_cost, off_peak_cost, budget_per_cycle, cost_coef, prediction_mode):
        self.interval_hour = interval_hour
        self.peak_cost = peak_cost
        self.off_peak_cost = off_peak_cost
        self.budget_per_cycle = budget_per_cycle
        self.cost_coef = cost_coef
        self.prediction_mode = prediction_mode
