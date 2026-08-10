from skill_extractor import extract_skills
from skill_matching import calculate_skill_match


# --------------------------------------------------
# FILE PATHS
# --------------------------------------------------

resume_path = "data/resumes/candidate_03.pdf"

skills_path = "data/skills.csv"


# --------------------------------------------------
# READ RESUME
# --------------------------------------------------

from pdf_parser import extract_text_from_pdf

resume_text = extract_text_from_pdf(
    resume_path
)


# --------------------------------------------------
# EXTRACT CANDIDATE SKILLS
# --------------------------------------------------

candidate_skills = extract_skills(
    resume_text,
    skills_path
)


# --------------------------------------------------
# REQUIRED ML ENGINEER SKILLS
# --------------------------------------------------

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


# --------------------------------------------------
# CALCULATE MATCH
# --------------------------------------------------

score, matched, missing = calculate_skill_match(
    candidate_skills,
    required_skills
)


# --------------------------------------------------
# DISPLAY RESULT
# --------------------------------------------------

print("\n========================================")

print("          SKILL MATCH ANALYSIS")

print("========================================")


print("\nCandidate Skills:")

for skill in candidate_skills:
    print("-", skill)


print("\nMatched Required Skills:")

for skill in matched:
    print("✓", skill)


print("\nMissing Required Skills:")

for skill in missing:
    print("✗", skill)


print("\nSkill Match Score:")

print(
    score,
    "%"
)


print("\n========================================")