from parameters import NUMBER_OF_QUARTERS, EURO_AREA_GDP_GROWTH


def gdp_gap(scenario):
    """GDP level gap relative to the central scenario, quarter by quarter (constant after 9 quarters)."""
    # Hold the final calculated gap constant for the remaining simulation quarters.
    level = level_central = 1.0
    gaps = []
    for growth, central_growth in zip(EURO_AREA_GDP_GROWTH[scenario], EURO_AREA_GDP_GROWTH["central"]):
        level *= 1 + growth / 100
        level_central *= 1 + central_growth / 100
        gaps.append(level / level_central - 1)
    return gaps + [gaps[-1]] * (NUMBER_OF_QUARTERS - len(gaps))
