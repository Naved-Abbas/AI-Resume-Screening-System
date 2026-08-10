from pdf_parser import extract_text_from_pdf
from skill_extractor import extract_skills


# Resume PDF
pdf_path = "data/resumes/candidate_01.pdf"

# Skills CSV
skills_path = "data/skills.csv"


# Extract resume text
text = extract_text_from_pdf(pdf_path)


# Extract skills
skills = extract_skills(
    text,
    skills_path
)


print("\n========== DETECTED SKILLS ==========\n")

for skill in skills:
    print("-", skill)


print("\n======================================")

print(
    "\nTotal Skills:",
    len(skills)
)