
import numpy as np

from parameters import UNEMPLOYED_EXPONENT, UNEMPLOYMENT_RATE_BY_QUALIFICATION
from equations.hiring_chances import hiring_chances


# BLOCK 4 — LABOR-MARKET MATCHING AND UNEMPLOYED WORKER SELECTION.
def initialize_labor_markets(firms, share_unemployment, exponent=UNEMPLOYED_EXPONENT):
    """Initialize one labor market per qualification and calibrate its matching efficiency."""
    # Build the starting unemployment stock and matching strength separately
    # for each qualification group.
    markets_by_qualification = {}
    for qualification in (0, 1, 2):
        qualified_firms = [e for e in firms if e.qualification == qualification]
        employees = sum(e.employee_count for e in qualified_firms)

        # Unemployment rate = unemployed / (unemployed + employees), so solve for unemployed.
        rate = UNEMPLOYMENT_RATE_BY_QUALIFICATION[qualification]
        unemployed = round(rate / (1 - rate) * employees)

        # Each quarter, some employee separations enter unemployment.
        vacancies = sum(e.initial_vacancies for e in qualified_firms)
        arrivals_into_unemployment = share_unemployment * sum(
            e.separation_rate * e.employee_count for e in qualified_firms
        )

      
        # Calibrate m0 so matches equal unemployment arrivals and the initial market is stable.
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
    # Steps 8–9: hiring weights fall with unemployment duration; draw workers
    # without replacement and return their positions in the duration array.
    """Select workers without replacement, giving recent unemployed workers higher odds."""
    # Return the selected positions in the unemployed-worker duration array.
    if number <= 0:
        return np.array([], dtype=int)
    number = min(number, len(durations))
    # Weighted random ranking: draw u^(1/weight) and keep the largest draws.
    draws = random_numpy.random(len(durations)) ** (
        1 / hiring_chances(durations)
    )
    return np.argpartition(-draws, number - 1)[:number]


def allocate_hires(vacancies, efforts, matches, advantage, random_numpy):
    """Allocate exactly the market's matches among firm vacancies, weighted by effort."""
  
    # Put every open vacancy in a pool with its firm index and weight (1 or 1 + advantage).
    firm_for_vacancy = np.repeat(np.arange(len(vacancies)), vacancies)
    weight = np.repeat(1 + advantage * np.array(efforts), vacancies)
    if matches <= 0 or len(weight) == 0:
        return [0] * len(vacancies)
  
  
  
    # Draw exactly `matches` vacancies without replacement; larger weights have higher odds.
    draws = random_numpy.random(len(weight)) ** (1 / weight)
    filled = np.argpartition(-draws, matches - 1)[:matches]
    # Count how many of the selected vacancies belong to each firm.
    return np.bincount(firm_for_vacancy[filled], minlength=len(vacancies)).tolist()
