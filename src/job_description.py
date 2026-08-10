from pathlib import Path

from src.text_cleaner import clean_text


def load_job_description(file_path):
    """
    Load a job description from a text file.
    """

    path = Path(file_path)

    if not path.exists():

        raise FileNotFoundError(
            f"Job description not found: {file_path}"
        )

    text = path.read_text(
        encoding="utf-8"
    )

    return text


def clean_job_description(file_path):
    """
    Load and clean a job description.
    """

    text = load_job_description(
        file_path
    )

    cleaned_text = clean_text(
        text
    )

    return cleaned_text