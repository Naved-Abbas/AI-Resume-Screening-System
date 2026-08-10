import pandas as pd
import re


def load_skills(csv_path):
    """
    Load skills from skills.csv.
    Uses the first column of the CSV.
    """

    df = pd.read_csv(csv_path)

    # Use the first column
    skills = df.iloc[:, 0].dropna().astype(str)

    # Clean skills
    skills = [
        skill.strip().lower()
        for skill in skills
        if skill.strip()
    ]

    # Remove duplicates
    skills = sorted(
        set(skills),
        key=len,
        reverse=True
    )

    return skills


def extract_skills(text, csv_path):
    """
    Extract known skills from complete resume text.
    """

    skills = load_skills(csv_path)

    # Normalize resume text
    text = text.lower()

    # Normalize whitespace
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    found_skills = []

    for skill in skills:

        # Escape special characters such as
        # C++, C#, .NET, etc.
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text):

            found_skills.append(skill)

    return found_skills