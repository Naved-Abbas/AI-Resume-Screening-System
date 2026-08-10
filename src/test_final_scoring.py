from pdf_parser import extract_text_from_pdf
from similarity import calculate_similarity
from job_description import clean_job_description
from skill_extractor import extract_skills
from skill_matching import calculate_skill_match
from final_scoring import calculate_final_score


# ==================================================
# FILE PATHS
# ==================================================

resume_path = "data/resumes/candidate_03.pdf"

jd_path = "data/job_descriptions/ml_engineer.txt"

skills_path = "data/skills.csv"


# ==================================================
# REQUIRED JOB SKILLS
# ==================================================

required_skills = [
    "Python",
    "Machine Learning",
    "NumPy",
    "Pandas",
    "Scikit-learn",
    "TensorFlow",
    "SQL",
    "NLP",
    "Git",
    "GitHub"
]


# ==================================================
# EXTRACT RESUME
# ==================================================

resume_text = extract_text_from_pdf(
    resume_path
)


# ==================================================
# CLEAN JOB DESCRIPTION
# ==================================================

cleaned_jd = clean_job_description(
    jd_path
)


# ==================================================
# TEXT SIMILARITY
# ==================================================

from text_cleaner import clean_text

cleaned_resume = clean_text(
    resume_text
)

similarity_score = calculate_similarity(
    cleaned_resume,
    cleaned_jd
)


# ==================================================
# EXTRACT CANDIDATE SKILLS
# ==================================================

candidate_skills = extract_skills(
    resume_text,
    skills_path
)


# ==================================================
# SKILL MATCH
# ==================================================

skill_score, matched_skills, missing_skills = (
    calculate_skill_match(
        candidate_skills,
        required_skills
    )
)


# ==================================================
# FINAL SCORE
# ==================================================

final_score = calculate_final_score(
    similarity_score,
    skill_score
)


# ==================================================
# DISPLAY RESULTS
# ==================================================

print("\n==========================================")

print("        FINAL CANDIDATE ANALYSIS")

print("==========================================")

print(
    "\nCandidate:",
    resume_path
)

print(
    "\nText Similarity:",
    similarity_score,
    "%"
)

print(
    "Skill Match:",
    skill_score,
    "%"
)

print(
    "\nMatched Skills:"
)

for skill in matched_skills:
    print(
        "✓",
        skill
    )

print(
    "\nMissing Skills:"
)

for skill in missing_skills:
    print(
        "✗",
        skill
    )

print(
    "\n------------------------------------------"
)

print(
    "FINAL CANDIDATE SCORE:",
    final_score,
    "%"
)

print(
    "------------------------------------------"
)

print(
    "\n=========================================="
)