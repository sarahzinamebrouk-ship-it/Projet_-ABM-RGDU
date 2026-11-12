import numpy as np
import random
from equations.hiring_chances import hiring_chances as chance_hire
from parameters import (
    EFFORT_ADVANTAGE,
    MODEL_SCALE,
    ELASTICITY_AT_MIN_WAGE,
    AVERAGE_EMPLOYMENT_2025_THOUSANDS,
    EXPLORATION,
    UNEMPLOYED_EXPONENT,
    PERMANENT_CONTRACT_ENDINGS_2025,
    LEARNING_GAIN,
    EMPLOYEES_BY_SIZE,
    SEPARATIONS_TO_UNEMPLOYMENT_SHARE,
    EFFORT_PENALTY,
    QUALIFICATION_BY_WAGE_LEVEL,
    WAGE_LEVEL_DISTRIBUTION,
    NATIONAL_WAGES_IN_MIN_WAGES,
    OVERALL_NET_WAGE,
    NET_WAGE_BY_SECTOR,
    UNEMPLOYMENT_TO_INACTIVITY_RATE,
    INACTIVITY_TO_UNEMPLOYMENT_RATE,
    LAYOFF_RATE,
)

from parameters import SECTORS, FIRM_PROFILES, VACANCY_RATE
from model.entities import Firm
from model.scheduler import execute_quarters
from markets.labor_market import initialize_labor_markets
from equations.desired_employment_change import desired_employment_change

def build_firms(near_min_wage_value=None, distribution=None):
    """the 36 firms (6 SECTORS x 6 FIRM_PROFILES)."""
    firms = []
    for sector in SECTORS:
        for size, level in FIRM_PROFILES:
            firms.append(Firm(len(firms), sector, size, level, near_min_wage_value, distribution))
    for qualification in (0, 1, 2):
        qualified_firms = [e for e in firms if e.qualification == qualification]
        total_vacancies = VACANCY_RATE / (1 - VACANCY_RATE) * sum(e.employee_count for e in qualified_firms)
        total_separations = sum(e.separation_rate * e.employee_count for e in qualified_firms)
        for e in qualified_firms:
            e.initial_vacancies = total_vacancies * e.separation_rate * e.employee_count / total_separations
    return firms

def create_unemployed_agents(number, arrivals, random_numpy, exit_to_inactivity=0.0):
  
  
    exit_rate = min(1.0, arrivals / number + exit_to_inactivity) if number else 1.0
    return random_numpy.geometric(exit_rate, size=number) - 1

def select_hired_workers(durations, number, random_numpy):
  
  
  
    if number <= 0:
        return np.array([], dtype=int)
    draws = random_numpy.random(len(durations)) ** (1 / chance_hire(durations))
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

def create_numpy_rng(seed, stream_name):
    """Create a reproducible NumPy random-number stream."""
    seed_value = random.Random(f"{seed}-{stream_name}").getrandbits(64)
    return np.random.default_rng(seed_value)

def simulate(
    firms,
    policy,
    seed,
    learning=True,
    elasticity_at_min_wage=ELASTICITY_AT_MIN_WAGE,
    share_unemployment=SEPARATIONS_TO_UNEMPLOYMENT_SHARE,
    advantage=EFFORT_ADVANTAGE,
    penalty=EFFORT_PENALTY,
    LEARNING_GAIN=LEARNING_GAIN,
    exploration=EXPLORATION,
    exponent=UNEMPLOYED_EXPONENT,
    contribution_cut=0.0,
    gap_gdp=None,
    layoff_rate=LAYOFF_RATE,
    exit_to_inactivity=UNEMPLOYMENT_TO_INACTIVITY_RATE,
):
    """Model component description."""
  
  
    random_generators = {
        name: random.Random(f"{seed}-{name}")
        for name in ("separations", "rounding", "choice", "inactivity", "layoffs")
    }
    separation_rng = create_numpy_rng(seed, "separations_numpy")
    random_unemployed = create_numpy_rng(seed, "unemployed")
    random_exits = create_numpy_rng(seed, "exits")
    random_vacancies = create_numpy_rng(seed, "vacancies_filled")

  
    labor_markets = initialize_labor_markets(
        firms, share_unemployment, exponent
    )
    durations = {
        qualification: create_unemployed_agents(
            labor_markets[qualification]["unemployed"],
            labor_markets[qualification]["arrivals"],
            random_unemployed,
            exit_to_inactivity,
        )
        for qualification in (0, 1, 2)
    }
    separations_into_unemployment = {
        qualification: labor_markets[qualification]["unemployed"]
        for qualification in (0, 1, 2)
    }
    employment = [e.employee_count for e in firms]
  
    inactive_people = {
        qualification: round(
            exit_to_inactivity
            * separations_into_unemployment[qualification]
            / INACTIVITY_TO_UNEMPLOYMENT_RATE
        )
        for qualification in (0, 1, 2)
    }

  
    employment_desired = [
        e.employee_count
        * (1 + desired_employment_change(policy, e.wage_in_min_wages, e.reference_employee_count,
                                           elasticity_at_min_wage, contribution_cut))
        for e in firms
    ]
    expectations = [1.0 for _ in firms]
    scores = [[0.0, -penalty] for _ in firms]
    history = {"employment": [list(employment)], "unemployed": [sum(len(d) for d in durations.values())],
                  "long_term_unemployment": [], "laid_off": [], "efforts": [], "hires": [], "vacancies": [],
                  "exits_to_inactivity": [], "entries_from_inactivity": [], "inactive_people": [sum(inactive_people.values())]}

    return execute_quarters(
        firms=firms,
        labor_markets=labor_markets,
        durations=durations,
        inactive_people=inactive_people,
        employment=employment,
        employment_desired=employment_desired,
        expectations=expectations,
        scores=scores,
        history=history,
        random=random_generators,
        separation_rng=separation_rng,
        random_unemployed=random_unemployed,
        random_exits=random_exits,
        random_vacancies=random_vacancies,
        learning=learning,
        advantage=advantage,
        penalty=penalty,
        LEARNING_GAIN=LEARNING_GAIN,
        exploration=exploration,
        exponent=exponent,
        share_unemployment=share_unemployment,
        gap_gdp=gap_gdp,
        layoff_rate=layoff_rate,
        exit_to_inactivity=exit_to_inactivity,
    )


