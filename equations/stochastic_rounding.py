def stochastic_round(number, random):
  
  
    entier = int(number)
    return entier + (1 if random.random() < number - entier else 0)