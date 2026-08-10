import re

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


STOP_WORDS = set(stopwords.words("english"))

lemmatizer = WordNetLemmatizer()


def clean_text(text):
    """Clean resume text for NLP processing."""

    # 1. Lowercase
    text = text.lower()

    # 2. Remove email addresses
    text = re.sub(
        r"\S+@\S+",
        " ",
        text
    )

    # 3. Remove URLs
    text = re.sub(
        r"http\S+|www\S+",
        " ",
        text
    )

    # 4. Keep alphabetic characters and spaces
    text = re.sub(
        r"[^a-zA-Z\s]",
        " ",
        text
    )

    # 5. Remove extra spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    # 6. Tokenization
    words = text.split()

    # 7. Remove stopwords
    words = [
        word
        for word in words
        if word not in STOP_WORDS
    ]

    # 8. Lemmatization
    words = [
        lemmatizer.lemmatize(word)
        for word in words
    ]

    # Final cleaned text
    cleaned_text = " ".join(words)

    return cleaned_text


def get_tokens(text):
    """Return cleaned resume text as a list of tokens."""

    cleaned_text = clean_text(text)

    return cleaned_text.split()