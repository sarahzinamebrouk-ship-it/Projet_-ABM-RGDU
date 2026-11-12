import numpy as np

from parameters import HIRING_CHANCE_DECLINE, HIRING_CHANCE_DECLINE_QUARTERS


def hiring_chances(durations):
  
    return np.maximum(1 - HIRING_CHANCE_DECLINE, 1 - HIRING_CHANCE_DECLINE * durations / HIRING_CHANCE_DECLINE_QUARTERS)
