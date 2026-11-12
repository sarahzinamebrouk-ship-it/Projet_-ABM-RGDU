from parameters import LEARNING_GAIN

def update_score(legacy_score, outcome, LEARNING_GAIN=LEARNING_GAIN):
  
    return legacy_score + LEARNING_GAIN * (outcome - legacy_score)