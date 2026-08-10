import pandas as pd


def get_recommendation(score):
    """
    Convert final score into a recruiter-friendly recommendation.
    """

    if score >= 80:
        return "Highly Recommended"

    elif score >= 65:
        return "Recommended"

    elif score >= 50:
        return "Consider"

    else:
        return "Not Recommended"


def add_recommendations(ranking):
    """
    Add recommendation column to candidate ranking.
    """

    ranking = ranking.copy()

    ranking["Recommendation"] = ranking[
        "Final Score"
    ].apply(get_recommendation)

    return ranking