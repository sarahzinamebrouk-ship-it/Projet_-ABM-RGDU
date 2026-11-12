from parameters import T_MIN, T_DELTA_UNDER_50, T_DELTA_50_AND_OVER


def rgdu_relief_rate(wage_in_min_wages, employee_count):
    """Model component description."""
    if wage_in_min_wages <= 0 or wage_in_min_wages >= 3:
        return 0.0

    t_delta = T_DELTA_UNDER_50 if employee_count < 50 else T_DELTA_50_AND_OVER
    return T_MIN + t_delta * (0.5 * (3 / wage_in_min_wages - 1)) ** 1.75
