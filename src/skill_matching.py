def calculate_skill_match(
    candidate_skills,
    required_skills
):
    """
    Calculate how many required job skills
    are present in the candidate's skills.

    Returns:
        skill_score: percentage from 0 to 100
        matched_skills: skills candidate has
        missing_skills: skills candidate does not have
    """

    # Convert everything to lowercase
    candidate_set = {
        skill.lower().strip()
        for skill in candidate_skills
    }

    required_set = {
        skill.lower().strip()
        for skill in required_skills
    }

    # Avoid division by zero
    if not required_set:
        return 0.0, [], []

    # Find matched and missing skills
    matched = candidate_set.intersection(
        required_set
    )

    missing = required_set.difference(
        candidate_set
    )

    # Calculate percentage
    score = (
        len(matched) / len(required_set)
    ) * 100

    return (
        round(score, 2),
        sorted(matched),
        sorted(missing)
    )