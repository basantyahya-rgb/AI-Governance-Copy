
def make_decision(score):

    if score >= 70:
        return "BLOCK"

    elif score >= 30:
        return "REVIEW"

    return "ALLOW"