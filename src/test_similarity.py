from pdf_parser import extract_text_from_pdf
from text_cleaner import clean_text
from job_description import clean_job_description
from similarity import calculate_similarity


# --------------------------------------------------
# FILE PATHS
# --------------------------------------------------

resume_path = "data/resumes/candidate_01.pdf"

jd_path = "data/job_descriptions/python_developer.txt"


# --------------------------------------------------
# RESUME
# --------------------------------------------------

resume_text = extract_text_from_pdf(
    resume_path
)

cleaned_resume = clean_text(
    resume_text
)


# --------------------------------------------------
# JOB DESCRIPTION
# --------------------------------------------------

cleaned_jd = clean_job_description(
    jd_path
)


# --------------------------------------------------
# SIMILARITY
# --------------------------------------------------

score = calculate_similarity(
    cleaned_resume,
    cleaned_jd
)


# --------------------------------------------------
# RESULT
# --------------------------------------------------

print("\n====================================")

print("       RESUME MATCH ANALYSIS")

print("====================================")

print(
    "\nResume:",
    resume_path
)

print(
    "Job Description:",
    jd_path
)

print(
    "\nMatch Score:",
    score,
    "%"
)

print("\n====================================")