from job_description import (
    load_job_description,
    clean_job_description
)


jd_path = "data/job_descriptions/ml_engineer.txt"


# Load original JD
jd_text = load_job_description(
    jd_path
)


# Clean JD
cleaned_jd = clean_job_description(
    jd_path
)


print("\n========== JOB DESCRIPTION ==========\n")

print(jd_text)


print("\n========== CLEANED JOB DESCRIPTION ==========\n")

print(cleaned_jd)