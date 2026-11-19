from parameters import LEARNING_GAIN

def update_score(legacy_score, outcome, LEARNING_GAIN=LEARNING_GAIN):
    # Retain the previous score while giving the latest outcome some weight.
    # Example: old score 0.0, outcome 0.15, gain 0.10 -> new score 0.015.
    return legacy_score + LEARNING_GAIN * (outcome - legacy_score)
