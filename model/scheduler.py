
import numpy as np

from parameters import NUMBER_OF_QUARTERS, INACTIVITY_TO_UNEMPLOYMENT_RATE
from equations.stochastic_rounding import stochastic_round
from equations.expected_demand import expected_demand
from equations.effort_choice import choose_effort
from equations.matching_function import number_of_matches
from equations.update_effort_score import update_score
from markets.labor_market import allocate_hires, select_hired_workers
from equations.effort_score import effort_score
from model.collector import record_period



def execute_quarters(
    firms, labor_markets, durations, inactive_people, employment, employment_desired,
    expectations, scores, history, random, separation_rng, random_exits,
    random_unemployed, random_vacancies, share_unemployment, gap_gdp,
    exit_to_inactivity, layoff_rate, learning,
    advantage, penalty, LEARNING_GAIN, exploration, exponent,
):

  
  
  

    for quarter in range(1, NUMBER_OF_QUARTERS + 1):

      
      
      

        for qualification in (0, 1, 2):
            durations[qualification] = durations[qualification] + 1

        arrivals = {0: 0, 1: 0, 2: 0}

      
      
      

      
      

        exits, entries = 0, 0

        for qualification in (0, 1, 2):

            leave = (
                random_exits.random(len(durations[qualification]))
                < exit_to_inactivity
            )

            exits += int(leave.sum())

            durations[qualification] = durations[qualification][~leave]

          
          

            new_entrants = min(
                stochastic_round(
                    INACTIVITY_TO_UNEMPLOYMENT_RATE * inactive_people[qualification],
                    random["inactivity"]
                ),
                inactive_people[qualification]
            )

            inactive_people[qualification] += int(leave.sum()) - new_entrants

            entries += new_entrants

            durations[qualification] = np.concatenate([
                durations[qualification],
                np.zeros(new_entrants, dtype=int)
            ])

      
      
      

      
      

        for i, e in enumerate(firms):

            separating_workers = int(separation_rng.binomial(employment[i], e.separation_rate))
            to_unemployment = int(separation_rng.binomial(separating_workers, share_unemployment))

            employment[i] -= to_unemployment

            arrivals[e.qualification] += to_unemployment

      
      
      

      

        previous_gdp_gap = (
            0.0
            if gap_gdp is None or quarter == 1
            else gap_gdp[quarter - 2]
        )

        for i, e in enumerate(firms):

            expectations[i] = expected_demand(
                expectations[i],
                e.sector,
                previous_gdp_gap
            )

      
      
      

      
      

        quarterly_layoffs = 0

        for i, e in enumerate(firms):

            target_employment = (
                employment_desired[i] * expectations[i]
                + e.initial_vacancies
            )

            employment_excess = employment[i] - target_employment

            if layoff_rate > 0 and employment_excess > 0:

                laid_off = min(
                    stochastic_round(
                        layoff_rate * employment_excess,
                        random["layoffs"]
                    ),
                    employment[i]
                )

                employment[i] -= laid_off

                arrivals[e.qualification] += laid_off

                quarterly_layoffs += laid_off

      
      

        for qualification in (0, 1, 2):

            durations[qualification] = np.concatenate([
                durations[qualification],
                np.zeros(arrivals[qualification], dtype=int)
            ])

      
      
      

        vacancies = [
            stochastic_round(
                max(
                    0.0,
                    employment_desired[i] * expectations[i]
                    + e.initial_vacancies
                    - employment[i]
                ),
                random["rounding"]
            )
            for i, e in enumerate(firms)
        ]

      
      
      

      
      

        effort_draws = [
            random["choice"].random()
            for _ in firms
        ]

        efforts = [
            choose_effort(
                scores[i],
                effort_draws[i],
                exploration
            )
            if learning and vacancies[i] > 0
            else 0
            for i in range(len(firms))
        ]

      
      
      

      

        hires = [0] * len(firms)

        for qualification in (0, 1, 2):

            firm_indices = [
                i
                for i, e in enumerate(firms)
                if e.qualification == qualification
            ]

            vacancies_q = [
                vacancies[i]
                for i in firm_indices
            ]

            if sum(vacancies_q) == 0:
                continue

          

            vacancy_weights = [
                1 + advantage * efforts[i]
                for i in firm_indices
            ]

            efficiency = (
                sum(
                    p * w
                    for p, w in zip(vacancies_q, vacancy_weights)
                )
                / sum(vacancies_q)
            )

          

            matches = number_of_matches(
                labor_markets[qualification]["m0"],
                len(durations[qualification]),
                sum(vacancies_q),
                exponent,
                efficiency
            )

          

            hires_q = allocate_hires(
                vacancies_q,
                [efforts[i] for i in firm_indices],
                matches,
                advantage,
                random_vacancies
            )

            market_fill_rate = (
                sum(hires_q) / sum(vacancies_q)
            )

          

            for i, number in zip(firm_indices, hires_q):

                hires[i] = number

                employment[i] += number

                if (
                    learning
                    and vacancies[i] > 0
                    and market_fill_rate > 0
                ):

                    outcome = effort_score(
                        number,
                        vacancies[i],
                        market_fill_rate,
                        efforts[i],
                        penalty
                    )

                    scores[i][efforts[i]] = update_score(
                        scores[i][efforts[i]],
                        outcome,
                        LEARNING_GAIN
                    )

          
          
          

            hires_choisis = select_hired_workers(
                durations[qualification],
                sum(hires_q),
                random_unemployed
            )

            durations[qualification] = np.delete(
                durations[qualification],
                hires_choisis
            )

        history = record_period(
            history,
            employment,
            durations,
            quarterly_layoffs,
            efforts,
            vacancies,
            hires,
            exits,
            entries,
            inactive_people,
        )

    return history
