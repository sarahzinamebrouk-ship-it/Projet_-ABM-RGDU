      
      
from parameters import LONG_TERM_UNEMPLOYMENT_QUARTERS


def record_period(
    history, employment, durations, quarterly_layoffs,
    efforts, vacancies, hires, exits, entries, inactive_people
):
    total_unemployed = sum(len(d) for d in durations.values())
    long_term_unemployment = sum(
        int((d >= LONG_TERM_UNEMPLOYMENT_QUARTERS).sum())
        for d in durations.values()
    )

    history["employment"].append(list(employment))
    history["unemployed"].append(total_unemployed)
    history["long_term_unemployment"].append(
        long_term_unemployment / total_unemployed if total_unemployed else 0.0
    )
    history["laid_off"].append(quarterly_layoffs)
    history["efforts"].append(
        [e if p > 0 else None for e, p in zip(efforts, vacancies)]
    )
    history["hires"].append(list(hires))
    history["vacancies"].append(list(vacancies))
    history["exits_to_inactivity"].append(exits)
    history["entries_from_inactivity"].append(entries)
    history["inactive_people"].append(sum(inactive_people.values()))

    return history