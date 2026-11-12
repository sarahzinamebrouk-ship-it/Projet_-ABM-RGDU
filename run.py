import csv
import statistics

from parameters import (
    ASSUMPTIONS,
    SECTORS,
    FIRM_PROFILES,
    WAGE_LEVELS,
    EMPLOYEES_BY_SIZE,
    AVERAGE_EMPLOYMENT_2025_THOUSANDS,
    WAGE_LEVEL_DISTRIBUTION,
    TEST_WAGE_LEVEL_DISTRIBUTION,
    TOTAL_BASE_EMPLOYMENT,
    QUALIFICATION_BY_WAGE_LEVEL,
    MODEL_SCALE,
    NUMBER_OF_QUARTERS,
    GROSS_MIN_WAGE_2026,
    CONTRIBUTION_RATE,
)
from model.model import build_firms, simulate
from equations.desired_employment_change import desired_employment_change
from equations.contribution_relief_choice import policy_relief_rate
from equations.gdp_gap import gdp_gap
from plot_outputs import create_charts
from excel_outputs import write_workbook


### Simulation and impact analysis

### Step 1: Baseline micro-level simulation with 36 representative firms

def simulate_economy():
    total_net_jobs = 0.0

    print(
        f"{'Sector':<30} | {'Size':<8} | {'Profile':<15} | "
        f"{'Wage (minimum wage)':<14} | {'Employment change (%)':<15} | {'Net jobs'}"
    )
    print("-" * 105)

    for sector in SECTORS:
        for size, level in FIRM_PROFILES:
            n_employees = EMPLOYEES_BY_SIZE[size]
            firm_temp = [f for f in firms if f.sector == sector and f.size == size and f.qualification == QUALIFICATION_BY_WAGE_LEVEL[level]][0]
            wage_in_min_wage = firm_temp.wage_in_min_wages

            emp_change_pct = desired_employment_change(
                "rgdu", wage_in_min_wage, n_employees
            )
            net_jobs_impact = n_employees * emp_change_pct
            total_net_jobs += net_jobs_impact

            print(
                f"{sector:<30} | {size:<8} | {level:<15} | "
                f"{wage_in_min_wage:<14.2f} | "
                f"{emp_change_pct * 100:<+14.2f}% | "
                f"{net_jobs_impact:<+11.1f}"
            )

    print("-" * 105)
    print(
        f"TOTAL ESTIMATED IMPACT ON EMPLOYMENT IN THE SIMULATION: "
        f"{total_net_jobs:+,.1f} jobs.\n"
    )


### Step 2: Weighted calculation at the national level

def simulate_macro_impact():
    total_jobs_created = 0.0

    print(
        f"{'Sector':<30} | {'Overall share':<12} | "
        f"{'Net national effect (jobs)'}"
    )
    print("-" * 65)

    for sector in SECTORS:
        sector_employment = AVERAGE_EMPLOYMENT_2025_THOUSANDS[sector] * 1000
        sector_variation = 0.0

        for size, level in FIRM_PROFILES:
            n_employees = EMPLOYEES_BY_SIZE[size]
            firm_temp = [f for f in firms if f.sector == sector and f.size == size and f.qualification == QUALIFICATION_BY_WAGE_LEVEL[level]][0]
            wage_in_min_wage = firm_temp.wage_in_min_wages

            profile_share = WAGE_LEVEL_DISTRIBUTION[sector][level] / 2.0
            # ASSUMPTION: two profiles per wage level, with equal shares

            profile_employees = sector_employment * profile_share

            change_pct = desired_employment_change(
                "rgdu", wage_in_min_wage, n_employees
            )
            sector_variation += profile_employees * change_pct

        total_jobs_created += sector_variation
        overall_weight = sector_employment / TOTAL_BASE_EMPLOYMENT

        print(
            f"{sector:<30} | {overall_weight * 100:>10.1f}% | "
            f"{sector_variation:>+27.0f}"
        )

    print("-" * 65)
    print(
        f"TOTAL MACROECONOMIC IMPACT: {total_jobs_created:+,.0f} jobs "
        f"(out of {TOTAL_BASE_EMPLOYMENT:,.0f} employees across the 6 sectors).\n"
    )


# Simulation settings

NUM_REPETITIONS = 200
# ASSUMPTION: 200 simulations per scenario (to calculate a mean and confidence interval)

SEED = 2026


### Step 4: Run multiple simulations with common random seeds

def run_simulations(firms, count, scheme, **options):
    """Run multiple simulations using the same random seeds across all scenarios."""
    return [
        simulate(firms, scheme, SEED + r, **options)
        for r in range(count)
    ]


### Step 1: Preparation

SCHEME_NAMES = {
    "none": "No exemption",
    "legacy": "Previous scheme",
    "rgdu": "RGDU 2026",
}

NATIONAL = 1 / MODEL_SCALE
# One model employee represents 100 actual employees

NUM_REPETITIONS_ROBUSTNESS = 60
# Simulations per robustness test (section F)

NUM_REPETITIONS_SENSITIVITY = 100
# Simulations per learning parameter setting (section H)

firms = build_firms()

INITIAL_EMPLOYMENT = sum(
    f.employee_count for f in firms
)


### Step 2: Helper functions for calculating results

def mean(values):
    return sum(values) / len(values)


def confidence_interval(values):
    """Mean and 95% confidence interval for the mean."""
    center = mean(values)
    margin = 1.96 * statistics.stdev(values) / len(values) ** 0.5

    return center, center - margin, center + margin


def summarize(values):
    """Mean [95% confidence interval for the mean], at the national level."""
    center, low, high = confidence_interval(values)

    return (
        f"{center * NATIONAL:9.0f}   "
        f"[{low * NATIONAL:8.0f} ; {high * NATIONAL:8.0f}]"
    )


def employment_differences(simulations_a, simulations_b, quarter, indices=None):
    """Employment difference between two scenarios, simulation by simulation."""
    indices = indices if indices is not None else range(len(firms))

    return [
        sum(
            a["employment"][quarter][i] - b["employment"][quarter][i]
            for i in indices
        )
        for a, b in zip(simulations_a, simulations_b)
    ]


def unemployment_differences(simulations_a, simulations_b, quarter):
    """Difference in the number of unemployed people between two scenarios."""
    return [
        a["unemployed"][quarter] - b["unemployed"][quarter]
        for a, b in zip(simulations_a, simulations_b)
    ]


def intensive_effort_share(simulations, quarter, size=None):
    """Share of firms recruiting through intensive effort."""

    efforts = [
        s["efforts"][quarter - 1][i]
        for s in simulations
        for i, f in enumerate(firms)
        if (size is None or f.size == size)
        and s["efforts"][quarter - 1][i] is not None
    ]

    return mean(efforts) if efforts else 0.0


def state_cost(simulation, scheme, contribution_reduction=0.0):
    """Annual uncollected contributions, in millions of euros."""

    total = 0.0

    for f, n in zip(
        firms,
        simulation["employment"][NUMBER_OF_QUARTERS]
    ):
        reduction = policy_relief_rate(
            scheme,
            f.wage_in_min_wages,
            f.reference_employee_count
        )

        reduction = reduction + contribution_reduction * (
            CONTRIBUTION_RATE - reduction
        )

        total += (
            n
            * f.wage_in_min_wages
            * GROSS_MIN_WAGE_2026
            * reduction
            * 12
        )

    return total * NATIONAL / 1e6


### Step 3: A. The three policy schemes (BASE scenario: no learning)

print(
    f"A. THE THREE POLICY SCHEMES "
    f"(baseline scenario without learning, T60, "
    f"{NUM_REPETITIONS} simulations, national level)"
)

print("   Mean [95% confidence interval for the mean]")

# Each scheme is simulated using the same random seeds.
# Differences therefore do not come from random variation.

results = {
    s: run_simulations(
        firms,
        NUM_REPETITIONS,
        s,
        learning=False
    )
    for s in SCHEME_NAMES
}

costs = {
    s: mean([
        state_cost(sim, s)
        for sim in simulations
    ])
    for s, simulations in results.items()
}

for s, simulations in results.items():
    print(
        f"  {SCHEME_NAMES[s]:18s} additional unemployed: "
        f"{summarize([sim['unemployed'][NUMBER_OF_QUARTERS] - sim['unemployed'][0] for sim in simulations])} "
        f"   gross cost: {costs[s]:7.0f} M euros/year"
    )

print(
    "  RGDU - previous scheme, jobs:",
    summarize(
        employment_differences(
            results["rgdu"],
            results["legacy"],
            NUMBER_OF_QUARTERS
        )
    )
)

print(
    "  RGDU - previous scheme, unemployed:",
    summarize(
        unemployment_differences(
            results["rgdu"],
            results["legacy"],
            NUMBER_OF_QUARTERS
        )
    )
)

print(
    "  No exemption - previous scheme, jobs:",
    summarize(
        employment_differences(
            results["none"],
            results["legacy"],
            NUMBER_OF_QUARTERS
        )
    )
)

print(
    "  No exemption - previous scheme, unemployed:",
    summarize(
        unemployment_differences(
            results["none"],
            results["legacy"],
            NUMBER_OF_QUARTERS
        )
    )
)

print(
    f"  RGDU - previous scheme gross cost: "
    f"{costs['rgdu'] - costs['legacy']:+.0f} M euros/year"
)


### Step 4: B. A general reduction in employer contributions

print(
    "\nB. GENERAL REDUCTION IN EMPLOYER CONTRIBUTIONS "
    "(starting from the previous scheme, baseline without learning, T60, national level)"
)

# We reduce the remaining employer contributions by 10%, 20% or 40% for all wages.

reductions = {}

for reduction_rate in (0.10, 0.20, 0.40):
    reductions[reduction_rate] = run_simulations(
        firms,
        NUM_REPETITIONS,
        "legacy",
        learning=False,
        contribution_cut=reduction_rate,
    )

    print(
        f"  reduction of {reduction_rate:.0%}: "
        f"jobs {summarize(employment_differences(reductions[reduction_rate], results['legacy'], NUMBER_OF_QUARTERS))}"
        f"   unemployed {summarize(unemployment_differences(reductions[reduction_rate], results['legacy'], NUMBER_OF_QUARTERS))}"
    )


### Step 5: C. Who gains and who loses under the RGDU? (mechanism)

print(
    "\nC. RGDU - PREVIOUS SCHEME BY WAGE LEVEL "
    "(baseline, T60, jobs, national level)"
)

for level in WAGE_LEVELS:
    indices = [
        f.index
        for f in firms
        if f.qualification == QUALIFICATION_BY_WAGE_LEVEL[level]
    ]

    print(
        f"  {level:16s}: "
        f"{summarize(employment_differences(results['rgdu'], results['legacy'], NUMBER_OF_QUARTERS, indices))}"
    )

print("  By sector (mean [confidence interval]):")

for sector in SECTORS:
    indices = [
        f.index
        for f in firms
        if f.sector == sector
    ]

    print(
        f"    {sector:30s} "
        f"{summarize(employment_differences(results['rgdu'], results['legacy'], NUMBER_OF_QUARTERS, indices))}"
    )


### Step 6: D. Behavioural learning effect: without learning (baseline) and with learning (alternative)

print(
    "\nD. RGDU EFFECT (RGDU - previous scheme) "
    "WITHOUT AND WITH LEARNING (jobs, national level)"
)

without_learning = {
    s: results[s]
    for s in ("legacy", "rgdu")
}

with_learning = {
    s: run_simulations(firms, NUM_REPETITIONS, s)
    for s in ("legacy", "rgdu")
}

for label, group in (
    ("without learning", without_learning),
    ("with learning", with_learning)
):
    for q in (4, 20, 60):
        print(
            f"  {label}, quarter {q:2d}: "
            f"{summarize(employment_differences(group['rgdu'], group['legacy'], q))}"
        )

print(
    "  Additional jobs due to learning alone "
    "(previous scheme, with learning - without learning):"
)

for q in (4, 20, 60):
    print(
        f"    quarter {q:2d}: "
        f"{summarize(employment_differences(with_learning['legacy'], without_learning['legacy'], q))}"
    )

print("  Share of firms using intensive effort (RGDU):")

for q in (1, 5, 20, 60):
    print(
        f"    quarter {q:2d}: "
        + "  ".join(
            f"{size} {intensive_effort_share(with_learning['rgdu'], q, size):.2f}"
            for size in ("Small", "Medium", "Large")
        )
    )


### Step 7: E. A severe demand shock (baseline without learning)

print(
    "\nE. SEVERE DEMAND SHOCK: jobs lost compared with the central scenario "
    "(baseline, T60, national level)"
)

shock = {}

for s in ("legacy", "rgdu"):
    shock[s] = run_simulations(
        firms,
        NUM_REPETITIONS,
        s,
        learning=False,
        gap_gdp=gdp_gap("severe")
    )

    print(
        f"  {SCHEME_NAMES[s]:18s}: "
        f"{summarize(employment_differences(shock[s], results[s], NUMBER_OF_QUARTERS))}"
    )

print(
    "  RGDU - previous scheme under shock:",
    summarize(
        employment_differences(
            shock["rgdu"],
            shock["legacy"],
            NUMBER_OF_QUARTERS
        )
    )
)


### Step 8: F. Robustness of parameters unrelated to learning (baseline without learning)

print(
    f"\nF. ROBUSTNESS: RGDU - previous scheme at quarter 60 "
    f"({NUM_REPETITIONS_ROBUSTNESS} simulations per test, "
    f"baseline without learning, national level)"
)

print(
    "   (Layoffs are only triggered by a severe shock: "
    "they are tested in section G)"
)

# We change ONE parameter at a time and examine whether the RGDU effect changes significantly.

tests = [("central", {}, {})]

tests += [
    (f"minimum wage elasticity {v}", {"elasticity_at_min_wage": v}, {})
    for v in (-0.2, -0.6)
]

tests += [
    (f"transitions to unemployment {v}", {"share_unemployment": v}, {})
    for v in (0.20, 0.50)
]

tests += [
    (f"transition to inactivity {v}", {"exit_to_inactivity": v}, {})
    for v in (0.0, 0.10, 0.30)
]

tests += [
    ("unemployment exponent 0.7", {"exponent": 0.7}, {})
]

tests += [
    (f"'Close to minimum wage' = {v} minimum wages", {}, {"near_min_wage_value": v})
    for v in (1.1, 1.3)
]

tests += [
    (
        "group distribution by sector",
        {},
        {"distribution": TEST_WAGE_LEVEL_DISTRIBUTION}
    )
]

for test_name, sim_options, firm_options in tests:
    test_firms = build_firms(**firm_options)

    a = run_simulations(
        test_firms,
        NUM_REPETITIONS_ROBUSTNESS,
        "rgdu",
        learning=False,
        **sim_options
    )

    b = run_simulations(
        test_firms,
        NUM_REPETITIONS_ROBUSTNESS,
        "legacy",
        learning=False,
        **sim_options
    )

    print(
        f"  {test_name:<46} "
        f"jobs {summarize(employment_differences(a, b, NUMBER_OF_QUARTERS))} "
        f"   unemployed {summarize(unemployment_differences(a, b, NUMBER_OF_QUARTERS))}"
    )


# Contribution rate: change the constant and then restore its original value.

initial_contribution_rate = CONTRIBUTION_RATE

for v in (0.44, 0.47):
    CONTRIBUTION_RATE = v

    a = run_simulations(
        firms,
        NUM_REPETITIONS_ROBUSTNESS,
        "rgdu",
        learning=False
    )

    b = run_simulations(
        firms,
        NUM_REPETITIONS_ROBUSTNESS,
        "legacy",
        learning=False
    )

    print(
        f"  {'contribution rate ' + str(v):<46} "
        f"jobs {summarize(employment_differences(a, b, NUMBER_OF_QUARTERS))} "
        f"   unemployed {summarize(unemployment_differences(a, b, NUMBER_OF_QUARTERS))}"
    )

CONTRIBUTION_RATE = initial_contribution_rate


### Step 8bis: G. Layoffs (only triggered by a severe fall in demand)

print(
    "\nG. SEVERE 10% GDP DROP: layoffs and job losses "
    "(national level, previous scheme, baseline)"
)

sharp_drop = [-0.10] * NUMBER_OF_QUARTERS

reference = run_simulations(
    firms,
    20,
    "legacy",
    learning=False
)

for speed in (0.0, 0.25, 1.0):
    simulations = run_simulations(
        firms,
        20,
        "legacy",
        learning=False,
        gap_gdp=sharp_drop,
        layoff_rate=speed
    )

    laid_off = mean([
        sum(sim["laid_off"])
        for sim in simulations
    ]) * NATIONAL

    print(
        f"  layoffs at {speed:.0%} of excess / quarter: "
        f"total layoffs {laid_off:8.0f} "
        f"   jobs lost T4 {mean(employment_differences(simulations, reference, 4)) * NATIONAL:9.0f} "
        f"   T60 {mean(employment_differences(simulations, reference, NUMBER_OF_QUARTERS)) * NATIONAL:9.0f}"
    )


### Step 8ter: H. Do the conclusions depend on learning parameters? (unsourced assumptions)

print(
    f"\nH. SENSITIVITY TO LEARNING PARAMETERS "
    f"(jobs at T60, {NUM_REPETITIONS_SENSITIVITY} simulations per row, national level)"
)

# A "parameter setting" = (name, simulation options).
# Each reform is compared with the previous scheme using THE SAME SETTINGS.

parameter_settings = [
    ("learning disabled (baseline)", {"learning": False}),
    ("central settings", {})
]

parameter_settings += [
    (f"effort advantage {v}", {"advantage": v})
    for v in (0.0, 0.25, 1.0)
]

parameter_settings += [
    (f"effort penalty {v}", {"penalty": v})
    for v in (0.05, 0.20)
]

parameter_settings += [
    (f"learning gain {v}", {"LEARNING_GAIN": v})
    for v in (0.05, 0.20)
]

parameter_settings += [
    (f"exploration {v}", {"exploration": v})
    for v in (0.05, 0.20)
]

reforms = [
    ("RGDU 2026 - legacy", {"policy": "rgdu"}),
    (
        "cut general of 10 %",
        {"policy": "legacy", "contribution_cut": 0.10}
    ),
    (
        "general reduction of 40%",
        {"policy": "legacy", "contribution_cut": 0.40}
    )
]

sensitivity = {
    reform_name: {}
    for reform_name, _ in reforms
}

# Reform -> parameter setting -> list of employment differences

print(
    f"  {'parameter setting':32s}"
    + "".join(
        f"{reform_name:>34s}"
        for reform_name, _ in reforms
    )
)

for setting_name, setting_options in parameter_settings:
    setting_reference = run_simulations(
        firms,
        NUM_REPETITIONS_SENSITIVITY,
        "legacy",
        **setting_options
    )

    row = f"  {setting_name:32s}"

    for reform_name, reform_settings in reforms:
        reform_settings = dict(reform_settings)
        policy = reform_settings.pop("policy")

        simulations = run_simulations(
            firms,
            NUM_REPETITIONS_SENSITIVITY,
            policy,
            **reform_settings,
            **setting_options
        )

        diffs = employment_differences(
            simulations,
            setting_reference,
            NUMBER_OF_QUARTERS
        )

        sensitivity[reform_name][setting_name] = diffs

        center, low, high = confidence_interval(diffs)

        row += (
            f"{center * NATIONAL:11.0f} "
            f"[{low * NATIONAL:8.0f};{high * NATIONAL:8.0f}]"
        )

    print(row)


### Step 8quater: I. FINAL TABLE

print(
    "\nI. FINAL TABLE (jobs and unemployed at T60, national level; "
    "mean [95% confidence interval for the mean])"
)

print(
    "   Baseline = without learning; cost is the PARTIAL GROSS COST "
    "(uncollected contributions), not the net cost to the State."
)

final_table_rows = []

# (name, simulations, general reduction, scheme, name in section H or None if not tested)

table_scenarios = [
    (
        "RGDU 2026 - legacy",
        results["rgdu"],
        0.0,
        "rgdu",
        "RGDU 2026 - legacy"
    ),
    (
        "General reduction of 10%",
        reductions[0.10],
        0.10,
        "legacy",
        "cut general of 10 %"
    ),
    (
        "General reduction of 20%",
        reductions[0.20],
        0.20,
        "legacy",
        None
    ),
    (
        "General reduction of 40%",
        reductions[0.40],
        0.40,
        "legacy",
        "general reduction of 40%"
    ),
    (
        "No exemption - previous scheme",
        results["none"],
        0.0,
        "none",
        None
    ),
]

for scenario_name, simulations, contribution_reduction, policy, sensitivity_name in table_scenarios:
    job_differences = employment_differences(
        simulations,
        results["legacy"],
        NUMBER_OF_QUARTERS,
    )

    unemployment_changes = unemployment_differences(
        simulations,
        results["legacy"],
        NUMBER_OF_QUARTERS,
    )
    jobs_mean, jobs_lower, jobs_upper = confidence_interval(job_differences)
    unemployed_mean, unemployed_lower, unemployed_upper = confidence_interval(
        unemployment_changes
    )
    jobs_summary = summarize(job_differences)
    unemployed_summary = summarize(unemployment_changes)

    cost_difference = mean([
        state_cost(sim, policy, contribution_reduction)
        for sim in simulations
    ]) - costs["legacy"]

    national_jobs_created = jobs_mean * NATIONAL

    # Gross cost per job: only if the reform costs money AND creates jobs.

    cost_per_job_k_euros = (
        cost_difference * 1e6 / national_jobs_created / 1000
        if cost_difference > 0 and national_jobs_created > 0
        else None
    )
    cost_per_job_text = (
        f"{cost_per_job_k_euros:.0f} k euros"
        if cost_per_job_k_euros is not None
        else "not applicable"
    )

    sensitivity_lower = None
    sensitivity_upper = None
    stable_sign = "Not tested"
    sensitivity_text = "(not tested)"

    if sensitivity_name and sensitivity_name in sensitivity:
        sensitivity_means = {
            setting_name: mean(diffs) * NATIONAL
            for setting_name, diffs in sensitivity[sensitivity_name].items()
            if diffs
        }

        if sensitivity_means:
            sensitivity_lower = min(sensitivity_means.values())
            sensitivity_upper = max(sensitivity_means.values())
            stable_sign = (
                "Yes"
                if sensitivity_lower > 0 or sensitivity_upper < 0
                else "No"
            )
            sensitivity_text = (
                f"{sensitivity_lower:8.0f} to {sensitivity_upper:8.0f}; "
                f"stable sign: {stable_sign}"
            )

    print(f"  {scenario_name}")
    print(f"      jobs: {jobs_summary}   unemployed: {unemployed_summary}")
    print(
        f"      additional gross cost: {cost_difference:+7.0f} M euros/year "
        f"  per job created: {cost_per_job_text}"
    )
    print(
        f"      sensitivity to learning parameters (jobs): "
        f"{sensitivity_text}"
    )

    final_table_rows.append(
        [
            scenario_name,
            round(jobs_mean * NATIONAL),
            round(jobs_lower * NATIONAL),
            round(jobs_upper * NATIONAL),
            round(unemployed_mean * NATIONAL),
            round(unemployed_lower * NATIONAL),
            round(unemployed_upper * NATIONAL),
            round(cost_difference, 2),
            round(cost_per_job_k_euros, 2)
            if cost_per_job_k_euros is not None
            else "",
            round(sensitivity_lower)
            if sensitivity_lower is not None
            else "",
            round(sensitivity_upper)
            if sensitivity_upper is not None
            else "",
            stable_sign,
        ]
    )


final_table_headers = [
    "Scenario",
    "Jobs mean (national)",
    "Jobs 95% CI lower",
    "Jobs 95% CI upper",
    "Unemployed mean (national)",
    "Unemployed 95% CI lower",
    "Unemployed 95% CI upper",
    "Additional gross cost (million euros/year)",
    "Gross cost per job (thousand euros)",
    "Sensitivity jobs lower bound (national)",
    "Sensitivity jobs upper bound (national)",
    "Sensitivity sign stable",
]

with open(
    "outputs/final_table.csv",
    "w",
    newline="",
    encoding="utf-8-sig",
) as output_file:
    writer = csv.writer(output_file, delimiter=",")
    writer.writerow(final_table_headers)
    writer.writerows(final_table_rows)

### Step 9: Assumptions table and graphs

with open(
    "outputs/assumptions_and_sources.csv",
    "w",
    newline="",
    encoding="utf-8-sig",
) as output_file:
    writer = csv.writer(output_file, delimiter=",")
    assumption_headers = [
        "Assumption",
        "Type",
        "Justification",
        "Tested for robustness?",
    ]
    writer.writerow(assumption_headers)
    writer.writerows(ASSUMPTIONS)

write_workbook(
    "outputs/simulation_results.xlsx",
    [
        (
            "Final results",
            final_table_headers,
            final_table_rows,
            [34, 18, 18, 18, 24, 18, 18, 27, 25, 30, 30, 22],
        ),
        (
            "Assumptions and sources",
            assumption_headers,
            ASSUMPTIONS,
            [58, 26, 100, 26],
        ),
    ],
)


# Generate the four charts

create_charts(
    results=results,
    without_learning=without_learning,
    with_learning=with_learning,
    shock_results=shock,
    sensitivity_results=sensitivity,
    learning_settings=parameter_settings,
    initial_employment=INITIAL_EMPLOYMENT,
    national_scale=NATIONAL,
    policy_names=SCHEME_NAMES,
    mean_function=mean,
    confidence_interval_function=confidence_interval,
    employment_differences_function=employment_differences,
    intensive_effort_share_function=intensive_effort_share,
)
