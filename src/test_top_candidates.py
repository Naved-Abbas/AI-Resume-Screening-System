from ranking import rank_candidates
from recommender import add_recommendations
from top_candidates import get_top_candidates


# ==================================================
# PATHS
# ==================================================

resume_folder = "data/resumes"

job_description = (
    "data/job_descriptions/ml_engineer.txt"
)

skills_path = "data/skills.csv"


# ==================================================
# RANK ALL CANDIDATES
# ==================================================

ranking = rank_candidates(
    resume_folder,
    job_description,
    skills_path
)


# ==================================================
# ADD RECOMMENDATIONS
# ==================================================

ranking = add_recommendations(
    ranking
)


# ==================================================
# GET TOP 3
# ==================================================

top_3 = get_top_candidates(
    ranking,
    top_n=3
)


# ==================================================
# DISPLAY TOP 3
# ==================================================

print("\n")
print("=" * 100)

print(
    "                 TOP 3 CANDIDATES"
)

print("=" * 100)


print(
    top_3[
        [
            "Rank",
            "Candidate",
            "Text Similarity",
            "Skill Match",
            "Final Score",
            "Recommendation"
        ]
    ].to_string(index=False)
)


print("=" * 100)


# ==================================================
# DISPLAY SKILL ANALYSIS
# ==================================================

print("\n")
print("=" * 100)

print(
    "              TOP CANDIDATE SKILL ANALYSIS"
)

print("=" * 100)


for _, candidate in top_3.iterrows():

    print("\n")
    print(
        f"🏆 Rank {candidate['Rank']}: "
        f"{candidate['Candidate']}"
    )

    print(
        f"Final Score: "
        f"{candidate['Final Score']}%"
    )

    print(
        f"Recommendation: "
        f"{candidate['Recommendation']}"
    )

    print("\n✅ Matched Skills:")

    matched = candidate["Matched Skills"]

    if matched:

        for skill in matched.split(","):

            skill = skill.strip()

            if skill:
                print(
                    f"   ✓ {skill}"
                )

    else:

        print(
            "   No matched skills"
        )


    print("\n❌ Missing Skills:")

    missing = candidate["Missing Skills"]

    if missing:

        for skill in missing.split(","):

            skill = skill.strip()

            if skill:
                print(
                    f"   ✗ {skill}"
                )

    else:

        print(
            "   No missing skills"
        )

    print(
        "-" * 70
    )


# ==================================================
# SAVE TOP 3
# ==================================================

top_3.to_csv(
    "data/top_3_candidates.csv",
    index=False
)


print(
    "\n✅ Top 3 candidates saved to "
    "data/top_3_candidates.csv"
)