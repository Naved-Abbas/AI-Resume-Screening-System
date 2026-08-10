from pdf_parser import extract_text_from_pdf
from text_cleaner import clean_text, get_tokens


pdf_path = "data/resumes/candidate_01.pdf"


# Extract resume text
text = extract_text_from_pdf(pdf_path)


# Clean text
cleaned_text = clean_text(text)


# Get tokens
tokens = get_tokens(text)


print("\n========== CLEANED TEXT ==========\n")

print(cleaned_text)


print("\n========== TOKENS ==========\n")

print(tokens)


print("\n========== TOKEN COUNT ==========\n")

print(len(tokens))