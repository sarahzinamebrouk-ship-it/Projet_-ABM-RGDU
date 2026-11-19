def stochastic_round(number, random):
    # We cannot open 3.7 vacancies: open 3, plus 1 more in 70% of draws.
    # This keeps the expected value at 3.7 without systematic rounding bias.
    entier = int(number)
    return entier + (1 if random.random() < number - entier else 0)
