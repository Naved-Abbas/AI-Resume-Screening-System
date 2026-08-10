import re
import nltk

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


# ============================================================
# NLTK RESOURCE SETUP
# ============================================================

def setup_nltk_resources():

    # Stopwords
    try:
        stopwords.words("english")
    except LookupError:
        nltk.download(
            "stopwords",
            quiet=True
        )

    # WordNet
    try:
        from nltk.corpus import wordnet
        wordnet.synsets("test")
    except LookupError:
        nltk.download(
            "wordnet",
            quiet=True
        )


# Run NLTK setup
setup_nltk_resources()


# ============================================================
# STOPWORDS
# ============================================================

STOP_WORDS = set(
    stopwords.words("english")
)


# ============================================================
# LEMMATIZER
# ============================================================

lemmatizer = WordNetLemmatizer()


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text):
    """
    Clean resume text for NLP processing.
    """

    # Safety check
    if text is None:
        return ""

    if not isinstance(text, str):
        text = str(text)

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

    # 4. Keep letters, spaces and useful symbols
    text = re.sub(
        r"[^a-zA-Z\s+#.]",
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
    cleaned_words = []

    for word in words:

        try:
            word = lemmatizer.lemmatize(
                word
            )

        except LookupError:
            pass

        cleaned_words.append(word)

    # 9. Final text
    return " ".join(
        cleaned_words
    )


# ============================================================
# GET TOKENS
# ============================================================

def get_tokens(text):
    """
    Return cleaned resume text
    as a list of tokens.
    """

    cleaned_text = clean_text(
        text
    )

    return cleaned_text.split()