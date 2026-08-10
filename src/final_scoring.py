def calculate_final_score(
    similarity_score,
    skill_score
):
    """
    Calculate final candidate score.

    Weight:
    60% Text Similarity
    40% Skill Match
    """

    final_score = (
        similarity_score * 0.60
        +
        skill_score * 0.40
    )

    return round(
        final_score,
        2
    )