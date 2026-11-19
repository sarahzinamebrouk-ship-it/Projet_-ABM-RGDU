import numpy as np

from parameters import HIRING_CHANCE_DECLINE, HIRING_CHANCE_DECLINE_QUARTERS


def hiring_chances(durations):
    # Recent unemployed workers have weight 1; it declines to 0.55 after
    # three quarters, then remains constant.
    return np.maximum(1 - HIRING_CHANCE_DECLINE, 1 - HIRING_CHANCE_DECLINE * durations / HIRING_CHANCE_DECLINE_QUARTERS)
