"""Create and save the simulation charts."""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from parameters import NUMBER_OF_QUARTERS


PROJECT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIRECTORY = os.path.join(PROJECT_DIRECTORY, "outputs")
os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)


def save_chart(filename, figure=None):
    """Save a chart as a PNG file in the project's outputs folder."""
    if figure is None:
        figure = plt.gcf()

    output_path = os.path.join(OUTPUT_DIRECTORY, filename)
    figure.savefig(
        output_path,
        format="png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(figure)
    print(f"Chart saved: {output_path}")


def create_charts(
    results,
    without_learning,
    with_learning,
    shock_results,
    sensitivity_results,
    learning_settings,
    initial_employment,
    national_scale,
    policy_names,
    mean_function,
    confidence_interval_function,
    employment_differences_function,
    intensive_effort_share_function,
):
    """Create the four charts used to summarize the simulation results."""
    for policy in ("legacy", "rgdu"):
        if policy not in results:
            raise KeyError(f"Policy missing from baseline results: {policy}")
        if policy not in shock_results:
            raise KeyError(f"Policy missing from demand-shock results: {policy}")

    for result_group in (without_learning, with_learning):
        for policy in ("legacy", "rgdu"):
            if policy not in result_group:
                raise KeyError(f"Policy missing from a learning group: {policy}")

    quarters = range(NUMBER_OF_QUARTERS + 1)

    # Chart 1: RGDU employment effects with and without firm learning.
    plt.figure(figsize=(7, 4))
    for label, result_group in (
        ("Without learning (baseline)", without_learning),
        ("With learning", with_learning),
    ):
        series = [
            [
                value * national_scale
                for value in employment_differences_function(
                    result_group["rgdu"],
                    result_group["legacy"],
                    quarter,
                )
            ]
            for quarter in quarters
        ]
        bounds = [
            confidence_interval_function(values) if quarter else (0, 0, 0)
            for quarter, values in enumerate(series)
        ]
        plt.plot(quarters, [bound[0] for bound in bounds], label=label)
        plt.fill_between(
            quarters,
            [bound[1] for bound in bounds],
            [bound[2] for bound in bounds],
            alpha=0.15,
        )

    plt.axhline(0, color="grey", linewidth=0.8)
    plt.xlabel("Quarter")
    plt.ylabel("Jobs: RGDU minus legacy policy")
    plt.title("RGDU employment effect (mean and 95% confidence interval)")
    plt.legend()
    plt.tight_layout()
    save_chart("rgdu_employment_effect.png")

    # Chart 2: employment paths with and without the severe demand shock.
    plt.figure(figsize=(7, 4))
    for policy in ("legacy", "rgdu"):
        shock_path = [
            mean_function(
                [
                    sum(simulation["employment"][quarter]) - initial_employment
                    for simulation in shock_results[policy]
                ]
            )
            * national_scale
            for quarter in quarters
        ]
        baseline_path = [
            mean_function(
                [
                    sum(simulation["employment"][quarter]) - initial_employment
                    for simulation in results[policy]
                ]
            )
            * national_scale
            for quarter in quarters
        ]
        plt.plot(
            quarters,
            shock_path,
            label=f"{policy_names[policy]} (severe shock)",
        )
        plt.plot(
            quarters,
            baseline_path,
            "--",
            label=f"{policy_names[policy]} (without shock)",
        )

    plt.xlabel("Quarter")
    plt.ylabel("Jobs gained since the start")
    plt.title("Severe demand shock (baseline without learning)")
    plt.legend()
    plt.tight_layout()
    save_chart("demand_shock.png")

    # Chart 3: share of firms using intensive recruitment effort.
    plt.figure(figsize=(7, 4))
    for firm_size in ("Small", "Medium", "Large"):
        plt.plot(
            range(1, NUMBER_OF_QUARTERS + 1),
            [
                intensive_effort_share_function(
                    with_learning["rgdu"],
                    quarter,
                    firm_size,
                )
                for quarter in range(1, NUMBER_OF_QUARTERS + 1)
            ],
            label=f"{firm_size} firms",
        )

    plt.xlabel("Quarter")
    plt.ylabel("Share using intensive recruitment effort")
    plt.title("Firms learn to recruit more intensively")
    plt.legend()
    plt.tight_layout()
    save_chart("recruitment_learning.png")

    # Chart 4: sensitivity of reform effects to learning settings.
    setting_names = [name for name, _ in learning_settings]
    reforms_to_plot = (
        "RGDU 2026 - legacy",
        "cut general of 10 %",
    )

    for reform_name in reforms_to_plot:
        if reform_name not in sensitivity_results:
            raise KeyError(
                f"Reform missing from sensitivity results: {reform_name}"
            )
        for setting_name in setting_names:
            if setting_name not in sensitivity_results[reform_name]:
                raise KeyError(
                    f"Learning setting missing: {setting_name} for {reform_name}"
                )

    figure, axes = plt.subplots(1, 2, figsize=(9, 4), sharey=True)
    for axis, reform_name in zip(axes, reforms_to_plot):
        interval_values = [
            confidence_interval_function(
                sensitivity_results[reform_name][setting_name]
            )
            for setting_name in setting_names
        ]
        axis.errorbar(
            [value[0] * national_scale for value in interval_values],
            range(len(setting_names)),
            xerr=[
                [
                    (value[0] - value[1]) * national_scale
                    for value in interval_values
                ],
                [
                    (value[2] - value[0]) * national_scale
                    for value in interval_values
                ],
            ],
            fmt="o",
            capsize=3,
        )
        axis.axvline(0, color="grey", linewidth=0.8)
        axis.set_title(reform_name, fontsize=9)
        axis.set_xlabel("Additional jobs at quarter 60 (95% CI)")

    axes[0].set_yticks(range(len(setting_names)))
    axes[0].set_yticklabels(setting_names, fontsize=7)
    figure.suptitle("Employment effects across learning settings")
    plt.tight_layout()
    save_chart("learning_sensitivity.png", figure)

    print("All four charts were generated successfully.")
    print(f"Output folder: {OUTPUT_DIRECTORY}")


if __name__ == "__main__":
    raise SystemExit(
        "Charts require simulation results. Run the project using: python run.py"
    )
