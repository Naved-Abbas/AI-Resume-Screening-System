from pdf_parser import extract_text_from_pdf


pdf_path = "data/resumes/candidate_01.pdf"

text = extract_text_from_pdf(pdf_path)

print("========== EXTRACTED RESUME TEXT ==========")
print(text)
print("============================================")