import os
import pandas as pd

from src.pdf_parser import extract_text_from_pdf
from src.text_cleaner import clean_text
from src.job_description import clean_job_description
from src.similarity import calculate_similarity
from src.skill_extractor import extract_skills
from src.skill_matching import calculate_skill_match
from src.final_scoring import calculate_final_score


def rank_candidates(
    resume_folder,
    job_description_path,
    skills_path
):
    """
    Rank all candidates using:

    60% Text Similarity
    40% Skill Match
    """

    # --------------------------------------------------
    # Clean Job Description
    # --------------------------------------------------

    cleaned_jd = clean_job_description(
        job_description_path
    )

    # --------------------------------------------------
    # Read original Job Description
    # --------------------------------------------------

    with open(
        job_description_path,
        "r",
        encoding="utf-8"
    ) as file:

        jd_text = file.read()

    # --------------------------------------------------
    # Extract required skills from JD
    # --------------------------------------------------

    required_skills = extract_skills(
        jd_text,
        skills_path
    )

    print("\nRequired Job Skills:")

    for skill in required_skills:
        print("-", skill)

    # --------------------------------------------------
    # Store results
    # --------------------------------------------------

    results = []

    # --------------------------------------------------
    # Find PDF resumes
    # --------------------------------------------------

    pdf_files = sorted(
        [
            file
            for file in os.listdir(resume_folder)
            if file.lower().endswith(".pdf")
        ]
    )

    # --------------------------------------------------
    # Process candidates
    # --------------------------------------------------

    for filename in pdf_files:

        pdf_path = os.path.join(
            resume_folder,
            filename
        )

        try:

            # Extract resume text
            resume_text = extract_text_from_pdf(
                pdf_path
            )

            # Clean resume text
            cleaned_resume = clean_text(
                resume_text
            )

            # Text similarity
            similarity_score = calculate_similarity(
                cleaned_resume,
                cleaned_jd
            )

            # Extract candidate skills
            candidate_skills = extract_skills(
                resume_text,
                skills_path
            )

            # Skill matching
            (
                skill_score,
                matched_skills,
                missing_skills
            ) = calculate_skill_match(
                candidate_skills,
                required_skills
            )

            # Final score
            final_score = calculate_final_score(
                similarity_score,
                skill_score
            )

            # Store result
            results.append(
                {
                    "Candidate": filename,
                    "Text Similarity": similarity_score,
                    "Skill Match": skill_score,
                    "Final Score": final_score,
                    "Matched Skills": ", ".join(
                        matched_skills
                    ),
                    "Missing Skills": ", ".join(
                        missing_skills
                    )
                }
            )

        except Exception as error:

            print(
                f"Error processing {filename}: {error}"
            )

    # --------------------------------------------------
    # Create DataFrame
    # --------------------------------------------------

    ranking_df = pd.DataFrame(
        results
    )

    # --------------------------------------------------
    # Sort by Final Score
    # --------------------------------------------------

    if not ranking_df.empty:

        ranking_df = ranking_df.sort_values(
            by="Final Score",
            ascending=False
        )

        ranking_df = ranking_df.reset_index(
            drop=True
        )

        ranking_df.insert(
            0,
            "Rank",
            ranking_df.index + 1
        )

    return ranking_df