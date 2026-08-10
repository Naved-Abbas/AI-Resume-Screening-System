from pdf_parser import extract_text_from_pdf
from resume_parser import extract_section


pdf_path = "data/resumes/candidate_01.pdf"

text = extract_text_from_pdf(pdf_path)


projects = extract_section(
    text,
    "Projects"
)

certifications = extract_section(
    text,
    "Certifications"
)


print("\n========== PROJECTS ==========")

for item in projects:
    print("-", item)


print("\n====== CERTIFICATIONS ======")

for item in certifications:
    print("-", item)