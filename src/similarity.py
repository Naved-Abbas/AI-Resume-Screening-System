from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_similarity(resume_text, job_description):
    """
    Calculate similarity between a resume and
    a job description using TF-IDF and cosine similarity.

    Returns:
        score_percentage: similarity score from 0 to 100
    """

    documents = [
        resume_text,
        job_description
    ]

    # Convert text into TF-IDF vectors
    vectorizer = TfidfVectorizer()

    tfidf_matrix = vectorizer.fit_transform(
        documents
    )

    # Calculate cosine similarity
    similarity_matrix = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:2]
    )

    similarity_score = similarity_matrix[0][0]

    # Convert to percentage
    score_percentage = similarity_score * 100

    return round(
        score_percentage,
        2
    )