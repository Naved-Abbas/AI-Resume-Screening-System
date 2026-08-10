from src.pdf_parser import extract_text_from_pdf
from src.resume_parser import parse_resume


# ============================================================
# PDF PATH
# ============================================================

pdf_path = "data/resumes/candidate_01.pdf"


# ============================================================
# EXTRACT TEXT
# ============================================================

text = extract_text_from_pdf(pdf_path)


print("\n" + "=" * 60)
print("EXTRACTED TEXT CHECK")
print("=" * 60)

print("Text length:", len(text))

print("\nFirst 1500 characters:")
print(text[:1500])


# ============================================================
# PARSE RESUME
# ============================================================

resume = parse_resume(text)


print("\n" + "=" * 60)
print("PARSED RESUME")
print("=" * 60)


print("\nName:")
print(resume["name"] or "NOT DETECTED")


print("\nEmail:")
print(resume["email"] or "NOT DETECTED")


print("\nEducation:")
print(resume["education"] or "NOT DETECTED")


print("\nExperience:")
print(resume["experience"] or "NOT DETECTED")


print("\nProjects:")

if resume["projects"]:

    for project in resume["projects"]:
        print("-", project)

else:

    print("NOT DETECTED")


print("\nCertifications:")

if resume["certifications"]:

    for certification in resume["certifications"]:
        print("-", certification)

else:

    print("NOT DETECTED")


print("\n" + "=" * 60)