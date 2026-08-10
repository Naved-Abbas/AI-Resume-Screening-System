from src.ranking import rank_candidates
from src.recommender import add_recommendations


# ==================================================
# PATHS
# ==================================================

resume_folder = "data/resumes"

job_description = (
    "data/job_descriptions/ml_engineer.txt"
)

skills_path = "data/skills.csv"


# ==================================================
# RANK CANDIDATES
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
# DISPLAY RESULTS
# ==================================================

print("\n")
print("=" * 100)

print(
    "                 FINAL CANDIDATE RANKING"
)

print("=" * 100)

print(
    ranking[
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
# TOP CANDIDATE
# ==================================================

if not ranking.empty:

    top_candidate = ranking.iloc[0]

    print("\n🏆 TOP CANDIDATE")
    print("-" * 50)

    print(
        "Candidate:",
        top_candidate["Candidate"]
    )

    print(
        "Text Similarity:",
        top_candidate["Text Similarity"],
        "%"
    )

    print(
        "Skill Match:",
        top_candidate["Skill Match"],
        "%"
    )

    print(
        "Final Score:",
        top_candidate["Final Score"],
        "%"
    )

    print(
        "Recommendation:",
        top_candidate["Recommendation"]
    )


# ==================================================
# SAVE RESULT
# ==================================================

ranking.to_csv(
    "data/candidate_ranking.csv",
    index=False
)

print(
    "\n✅ Ranking saved to "
    "data/candidate_ranking.csv"
)