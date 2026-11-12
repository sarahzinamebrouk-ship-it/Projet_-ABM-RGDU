
import numpy as np

from parameters import UNEMPLOYED_EXPONENT, UNEMPLOYMENT_RATE_BY_QUALIFICATION
from equations.hiring_chances import hiring_chances


def initialize_labor_markets(firms, share_unemployment, exponent=UNEMPLOYED_EXPONENT):
    """Model component description."""
    markets_by_qualification = {}
    for qualification in (0, 1, 2):
        qualified_firms = [e for e in firms if e.qualification == qualification]
        employees = sum(e.employee_count for e in qualified_firms)

        rate = UNEMPLOYMENT_RATE_BY_QUALIFICATION[qualification]
        unemployed = round(rate / (1 - rate) * employees)

        vacancies = sum(e.initial_vacancies for e in qualified_firms)
        arrivals_into_unemployment = share_unemployment * sum(
            e.separation_rate * e.employee_count for e in qualified_firms
        )

      
        denominator = (
            (unemployed + arrivals_into_unemployment) ** exponent
            * (vacancies + arrivals_into_unemployment) ** (1 - exponent)
        )
        m0 = arrivals_into_unemployment / denominator if denominator > 0 else 0.0
        markets_by_qualification[qualification] = {
            "unemployed": unemployed,
            "m0": m0,
            "arrivals": arrivals_into_unemployment,
        }
    return markets_by_qualification


def select_hired_workers(durations, number, random_numpy):
    """Model component description."""
    if number <= 0:
        return np.array([], dtype=int)
    number = min(number, len(durations))
    draws = random_numpy.random(len(durations)) ** (
        1 / hiring_chances(durations)
    )
    return np.argpartition(-draws, number - 1)[:number]


def allocate_hires(vacancies, efforts, matches, advantage, random_numpy):
    """Model component description."""
  
    firm_for_vacancy = np.repeat(np.arange(len(vacancies)), vacancies)
    weight = np.repeat(1 + advantage * np.array(efforts), vacancies)
    if matches <= 0 or len(weight) == 0:
        return [0] * len(vacancies)
  
  
  
    draws = random_numpy.random(len(weight)) ** (1 / weight)
    filled = np.argpartition(-draws, matches - 1)[:matches]
  
    return np.bincount(firm_for_vacancy[filled], minlength=len(vacancies)).tolist()
