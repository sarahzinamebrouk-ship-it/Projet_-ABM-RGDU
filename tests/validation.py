

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from equations.contribution_relief_choice import policy_relief_rate
import random

from equations.stochastic_rounding import stochastic_round
from equations.legacy_relief import legacy_relief
from equations.rgdu_relief_rate import rgdu_relief_rate
from equations.contribution_relief_choice import policy_relief_rate
from equations.effort_choice import choose_effort
from equations.employment_elasticity import employment_elasticity
from equations.update_effort_score import update_score
from equations.desired_employment_change import desired_employment_change
import statistics
from equations.gdp_gap import gdp_gap
from model.model import build_firms, simulate
from parameters import NUMBER_OF_QUARTERS
from equations.effort_score import effort_score
import numpy as np

from parameters import (
    TOTAL_BASE_EMPLOYMENT,
    MODEL_SCALE,
    NUMBER_OF_QUARTERS,
    NATIONAL_WAGE_LEVEL_SHARES,
    UNEMPLOYMENT_TO_INACTIVITY_RATE,
    INACTIVITY_TO_UNEMPLOYMENT_RATE,
    VACANCY_RATE,LONG_TERM_UNEMPLOYMENT_SHARE,
    SEPARATIONS_TO_UNEMPLOYMENT_SHARE,
    UNEMPLOYMENT_RATE_BY_QUALIFICATION,
)
from markets.labor_market import initialize_labor_markets
from equations.hiring_chances import hiring_chances
from model.model import select_hired_workers
import numpy as np

from parameters import NUMBER_OF_QUARTERS
from equations.matching_function import number_of_matches
from markets.labor_market import allocate_hires


VALIDATION_SEED = 2026


def run(firms, number, policy, **options):
    return [
        simulate(firms, policy, VALIDATION_SEED + r, **options)
        for r in range(number)
    ]


check_results = []

def check(description, condition):
    """Record a check: OK when the condition is true, FAIL otherwise."""
    check_results.append(bool(condition))
    print(f"  [{'PASS' if condition else 'FAIL'}] {description}")

def unfilled_vacancies(simulation, quarter):
    """Vacancies still open at the end of a quarter (quarter = 1, 2, ..., 60)."""
    return sum(simulation["vacancies"][quarter - 1]) - sum(simulation["hires"][quarter - 1])

def vacancy_rate(simulation, quarter):
    """Unfilled vacancies divided by employees plus unfilled vacancies, matching the Dares vacancy-rate definition."""
    vacancies = unfilled_vacancies(simulation, quarter)
    return vacancies / (sum(simulation["employment"][quarter - 1]) + vacancies)

def _is_rejected(policy_name):
    try:
        policy_relief_rate(policy_name, 1.5, 20)
    except ValueError:
        return True
    return False

def check_model():
    print("CODE CHECKS (execution stops if a check fails)")
    firms = build_firms()
    separating_employees = sum(e.employee_count for e in firms)
    legacy = run(firms, 5, "legacy")
    rgdu = run(firms, 5, "rgdu")
    legacy_without_learning = run(firms, 5, "legacy", learning=False)

  
    check('RGDU relief is zero from 3 minimum wages onward', rgdu_relief_rate(3.0, 100) == 0.0)
    check('RGDU relief at the minimum wage equals 0.02 plus the size adjustment (0.3781 below 50 employees, 0.3821 otherwise)',
             abs(rgdu_relief_rate(1.0, 20) - 0.3981) < 1e-9 and abs(rgdu_relief_rate(1.0, 100) - 0.4021) < 1e-9)
    check('Legacy relief is positive at 3 minimum wages and zero from 3.4 minimum wages onward',
             legacy_relief(3.0, 20) > 0 and legacy_relief(3.4, 20) == 0.0)
    check('Employment elasticity is -0.6 at the minimum wage and -0.2 at 2 minimum wages (Bozio and Wasmer)',            abs(employment_elasticity(1.0) + 0.6) < 1e-9 and abs(employment_elasticity(2.0) + 0.2) < 1e-9)
    check('An unknown policy is rejected', _is_rejected("other"))
    check('RGDU increases desired employment at 1.5 minimum wages and decreases it at 2 minimum wages',
             desired_employment_change("rgdu", 1.5, 553) > 0 and desired_employment_change("rgdu", 2.0, 553) < 0)
    check('A larger general contribution cut increases desired employment',
             desired_employment_change("legacy", 1.5, 553, contribution_cut=0.2)
             > desired_employment_change("legacy", 1.5, 553, contribution_cut=0.1) > 0)
    draws = [stochastic_round(3.78, random.Random(draw_seed)) for draw_seed in range(20000)]
    check('Stochastic rounding is unbiased (the mean of 3.78 remains close to 3.78)', abs(sum(draws) / len(draws) - 3.78) < 0.02)

  
    check('Without exploration, the firm chooses the effort with the highest score (ties select standard effort)',             choose_effort([0.0, 0.3], 0.9) == 1 and choose_effort([0.0, -0.1], 0.9) == 0 and choose_effort([0.2, 0.2], 0.9) == 0)
    check('The effort score is zero when the firm performs like the market and equals the negative penalty under intensive effort',
             abs(effort_score(5, 10, 0.5, 0)) < 1e-9 and abs(effort_score(5, 10, 0.5, 1, 0.1) + 0.1) < 1e-9)
    check('The score update moves the score toward the latest outcome (0 to 0.1 with a learning gain of 0.1)', abs(update_score(0.0, 1.0, 0.1) - 0.1) < 1e-9)
    without_learning = simulate(firms, "rgdu", 7, learning=False)
    check('Without learning, no firm chooses intensive effort',
             sum(e for t in without_learning["efforts"] for e in t if e is not None) == 0)
    check('With learning, firms choose intensive effort',
             sum(e for t in rgdu[0]["efforts"] for e in t if e is not None) > 0)
    
  
    random_test = np.random.default_rng(3)
    vacancies_test, efforts_test = [5, 0, 12, 3], [1, 0, 0, 1]
    allocations = [allocate_hires(vacancies_test, efforts_test, matches, 0.5, random_test)
                for matches in range(0, 21) for _ in range(20)]
    check('Allocated hires exactly equal the number of market matches, with no loss or excess',
             all(sum(allocation) == matches for allocation, matches in zip(allocations, [r for r in range(0, 21) for _ in range(20)])))
    check('No firm receives more hires than its open vacancies',
             all(h <= p for allocation in allocations for h, p in zip(allocation, vacancies_test)))
    two_firms = np.array([allocate_hires([10, 10], [1, 0], 6, 0.5, random_test) for _ in range(3000)])
    check('With equal vacancies, the firm using intensive effort receives more hires than the firm using standard effort',             two_firms[:, 0].mean() > two_firms[:, 1].mean())
    check('More effort creates more total matches (efficiency 1.4 versus 1.0 in the same market)',
             number_of_matches(0.3, 100, 40, efficiency=1.4) > number_of_matches(0.3, 100, 40, efficiency=1.0))
    check('Matches never exceed the number of unemployed workers or vacancies',
             number_of_matches(5.0, 10, 40, efficiency=2.0) <= 10 and number_of_matches(5.0, 40, 10, efficiency=2.0) <= 10)
    check('With the same random seed, effort learning increases total employment (effort affects the market, not only allocation)',
             sum(sum(s["employment"][NUMBER_OF_QUARTERS]) for s in legacy) > sum(sum(s["employment"][NUMBER_OF_QUARTERS]) for s in legacy_without_learning))
    check('The model contains 36 firms', len(firms) == 36)
    check('No wage falls below the minimum wage', all(e.wage_in_min_wages >= 1.0 for e in firms))
    check('The model uses a 1/100 scale: simulated employees times 100 match employment in the six sectors within 1 percent',           abs(separating_employees / MODEL_SCALE / TOTAL_BASE_EMPLOYMENT - 1) < 0.01)
    check('Wage-level shares sum to 100 percent', abs(sum(NATIONAL_WAGE_LEVEL_SHARES.values()) - 1) < 1e-9)
    small = [e for e in firms if e.size == "Small"][0]
    check('The 50-employee threshold uses the reference firm size, not its scaled simulated headcount',
             small.reference_employee_count == 27 and small.employee_count > 27)
    check('Initial vacancies match the Dares total vacancy rate of 2.3 percent',
             abs(sum(e.initial_vacancies for e in firms) - VACANCY_RATE / (1 - VACANCY_RATE) * separating_employees) < 1e-6)

  
    check('A recently unemployed worker has weight 1; after 3 quarters it falls to 0.55 and then remains there',             abs(hiring_chances(np.array([0]))[0] - 1) < 1e-9
             and abs(hiring_chances(np.array([3]))[0] - 0.55) < 1e-9
             and abs(hiring_chances(np.array([10]))[0] - 0.55) < 1e-9)
    selected_workers = select_hired_workers(np.array([0] * 100 + [10] * 100), 50, random_test)
    check('The selection returns the requested number of distinct unemployed workers', len(selected_workers) == 50 and len(set(selected_workers)) == 50)
    recent_workers_selected = sum(1 for place in np.concatenate([select_hired_workers(np.array([0] * 100 + [10] * 100), 50, random_test) for _ in range(200)]) if place < 100)
    check('Recently unemployed workers are hired more often than the long-term unemployed', recent_workers_selected > 200 * 50 / 2)
    check('People are conserved: employees, unemployed workers, and inactive people have a constant total',
             all(
                 len({sum(s["employment"][t]) + s["unemployed"][t] + s["inactive_people"][t] for t in range(NUMBER_OF_QUARTERS + 1)}) == 1
                 for s in rgdu
             ))
    without_inactivity = simulate(firms, "legacy", 7, exit_to_inactivity=0.0)
    check('With a zero exit-to-inactivity rate, nobody enters or leaves inactivity and there are no inactive people',
             sum(without_inactivity["exits_to_inactivity"]) == 0 and sum(without_inactivity["entries_from_inactivity"]) == 0
             and without_inactivity["inactive_people"][0] == 0)
    check('At initialization, transitions balance: 5.8 percent of inactive people equals 22.7 percent of unemployed workers, within 1 percent',            abs(INACTIVITY_TO_UNEMPLOYMENT_RATE * rgdu[0]["inactive_people"][0] / (UNEMPLOYMENT_TO_INACTIVITY_RATE * rgdu[0]["unemployed"][0]) - 1) < 0.01)
    check('At the Insee exit-to-inactivity rate, unemployed workers leave unemployment (about 22.7 percent per quarter)',
             0.15 < sum(rgdu[0]["exits_to_inactivity"]) / NUMBER_OF_QUARTERS / rgdu[0]["unemployed"][0] < 0.30)
    check('No firm hires more workers than its open vacancies in the simulations',
             all(0 <= h <= p for s in rgdu for hs, ps in zip(s["hires"], s["vacancies"]) for h, p in zip(hs, ps)))

  
    check('The model runs for 60 quarters (61 values including the initial period)', len(legacy[0]["employment"]) == NUMBER_OF_QUARTERS + 1)
    check('The same random seed produces the same result', simulate(firms, "rgdu", 7) == simulate(firms, "rgdu", 7))
    check('Without reform or learning, employment remains stable (less than a 0.3 percent change after 15 years)',
             abs(sum(sum(s["employment"][NUMBER_OF_QUARTERS]) for s in legacy_without_learning) / 5 / separating_employees - 1) < 0.003)
    check('Without reform or learning, the vacancy rate stays close to the Dares figure of 2.3 percent',
             abs(statistics.mean(vacancy_rate(s, t) for s in legacy_without_learning for t in range(21, NUMBER_OF_QUARTERS + 1)) - VACANCY_RATE) < 0.002)
    none = run(firms, 5, "none")
    check('Without contribution relief, employment is lower and unemployment is higher than under the legacy policy',
             sum(sum(s["employment"][NUMBER_OF_QUARTERS]) for s in none) < sum(sum(s["employment"][NUMBER_OF_QUARTERS]) for s in legacy)
             and none[0]["unemployed"][NUMBER_OF_QUARTERS] > legacy[0]["unemployed"][NUMBER_OF_QUARTERS])
    check('The central GDP scenario has no gap from itself', max(abs(x) for x in gdp_gap("central")) == 0.0)
    shock = run(firms, 5, "legacy", learning=False, gap_gdp=gdp_gap("severe"))
    check('A severe demand shock lowers employment compared with the same scenario without the shock and with the same seeds',
             sum(sum(s["employment"][NUMBER_OF_QUARTERS]) for s in shock) < sum(sum(s["employment"][NUMBER_OF_QUARTERS]) for s in legacy_without_learning))
    sharp_drop = [-0.10] * NUMBER_OF_QUARTERS
    check('Layoffs are zero when the layoff rate is zero and occur after a sharp GDP decline when the rate is positive',
             sum(simulate(firms, "legacy", 7, gap_gdp=sharp_drop, layoff_rate=0.0)["laid_off"]) == 0
             and sum(simulate(firms, "legacy", 7, gap_gdp=sharp_drop, layoff_rate=0.25)["laid_off"]) > 0)
  
  
  
    reference = run(firms, 20, "legacy", learning=False)
    cut = run(firms, 20, "legacy", learning=False, contribution_cut=0.10)
    additional_desired_employment = sum(
        e.employee_count * desired_employment_change("legacy", e.wage_in_min_wages, e.reference_employee_count, contribution_cut=0.10)
        for e in firms
    )
    additional_observed_employment = statistics.mean(sum(a["employment"][NUMBER_OF_QUARTERS]) - sum(b["employment"][NUMBER_OF_QUARTERS]) for a, b in zip(cut, reference))
    check(f'After 15 years, observed additional employment is 85 to 105 percent of desired additional employment (observed: {additional_observed_employment / additional_desired_employment:.0%})',
             0.85 < additional_observed_employment / additional_desired_employment < 1.05)

national_validation_scale = 1 / MODEL_SCALE

def validate_model():
    firms = build_firms()
    without_learning = run(firms, 20, "legacy", learning=False)
    with_learning = run(firms, 20, "legacy")

    print("\nCALIBRATION (values set by the model; recovering them proves nothing)")
    for qualification in (0, 1, 2):
        employees = sum(e.employee_count for e in firms if e.qualification == qualification)
        unemployed = initialize_labor_markets(firms, SEPARATIONS_TO_UNEMPLOYMENT_SHARE)[qualification]["unemployed"]
        print(f"  Initial unemployment rate, qualification {qualification}: model {unemployed / (unemployed + employees):.1%}; Insee {UNEMPLOYMENT_RATE_BY_QUALIFICATION[qualification]:.1%}")
  
    rate = []
    for s in without_learning:
        for t in range(1, NUMBER_OF_QUARTERS + 1):
            arrivals = (s["unemployed"][t] - s["unemployed"][t - 1] + sum(s["hires"][t - 1])
                        + s["exits_to_inactivity"][t - 1] - s["entries_from_inactivity"][t - 1])
            rate.append(arrivals / sum(s["employment"][t - 1]))
    print(f"  Employment-to-unemployment transitions per quarter: model {statistics.mean(rate):.2%}; Insee 1.80 percent")

    print("\nINDEPENDENT VALIDATION (values not provided to the model)")
  
    long_term_share = statistics.mean(s["long_term_unemployment"][t] for s in without_learning for t in range(20, NUMBER_OF_QUARTERS))
    gap = long_term_share - LONG_TERM_UNEMPLOYMENT_SHARE
    print(f"  1. Long-term unemployment share: model {long_term_share:.1%}; Insee 2025 {LONG_TERM_UNEMPLOYMENT_SHARE:.1%}"
          f"   -> {'close' if abs(gap) < 0.05 else 'DEVIATION: model limitation'} (difference: {gap * 100:+.1f} percentage points)")
  
    vacancy_without = statistics.mean(
        vacancy_rate(s, t)
        for s in without_learning
        for t in range(20, NUMBER_OF_QUARTERS + 1)
    )
    vacancy_with = statistics.mean(
        vacancy_rate(s, t)
        for s in with_learning
        for t in range(20, NUMBER_OF_QUARTERS + 1)
    )
    print(f"  2. Vacancy rate after 5 years: without learning {vacancy_without:.2%}; with learning {vacancy_with:.2%}; Dares {VACANCY_RATE:.1%}")
    print("     (The vacancy rate is calibrated to 2.3 percent; staying near that value indicates model stability. With learning, firms fill more vacancies:")
    print("      this reflects the effort advantage, an unsupported assumption tested in section H.)")
  
    job_finding_rate = statistics.mean(sum(s["hires"][t - 1]) / s["unemployed"][t - 1] for s in without_learning for t in range(21, NUMBER_OF_QUARTERS + 1))
    print(f"  3. Quarterly job-finding rate: model {job_finding_rate:.0%}; Insee 2024: 27.0 percent; limitation: the model hires too slowly")
  
    print("  4. Employment dynamics after a demand shock (difference from the same scenario without a shock; 30 simulations; first 10 years):")
    for scenario_name, gap_gdp in (("shock severe (-1,3 % of gdp)", gdp_gap("severe")), ("sharp decline of 10 %", [-0.10] * NUMBER_OF_QUARTERS)):
        shock = run(firms, 30, "legacy", gap_gdp=gap_gdp)
        base = run(firms, 30, "legacy")
        additional_unemployed = [statistics.mean(c["unemployed"][t] - b["unemployed"][t] for c, b in zip(shock, base)) for t in range(1, 41)]
        additional_vacancies = [statistics.mean(unfilled_vacancies(c, t) - unfilled_vacancies(b, t) for c, b in zip(shock, base)) for t in range(1, 41)]
        correlation = statistics.correlation(additional_unemployed, additional_vacancies)
        peak_quarter = max(range(40), key=lambda t: additional_unemployed[t]) + 1
        print(f"     {scenario_name:28s}: additional unemployed workers at the peak {max(additional_unemployed) * national_validation_scale:8.0f} (quarter {peak_quarter}),"
              f" fewer vacancies {-min(additional_vacancies) * national_validation_scale:8.0f}, correlation {correlation:+.2f}"
              f"  -> {'expected direction (Beveridge curve)' if correlation < -0.5 and max(additional_unemployed) > 0 else 'ÉCART'}")
    print("     (Directional check only: unemployment rises while vacancies fall. Stylized facts: Dosi et al. 2018; Kant, Ballot and Goudet.)")

check_model()
failure_count = check_results.count(False)
print(f"\n=> {len(check_results) - failure_count} of {len(check_results)} checks passed")
if failure_count:
    raise SystemExit("A check failed; fix it before running the experiments.")
validate_model()
print()


    
