# 📄 AI Resume Screening & Candidate Recommendation System

An AI-powered resume screening and candidate recommendation system built with Python and Streamlit.

The system analyzes resumes, extracts candidate information and skills, compares resumes with job descriptions, ranks candidates, and provides recommendations.

## 🚀 Features

- 📄 PDF Resume Upload
- 👤 Candidate Information Extraction
- 📧 Email Detection
- 🎓 Education Extraction
- 💼 Experience Extraction
- 🚀 Project Extraction
- 🏆 Certification Extraction
- 💻 Skill Extraction
- 🎯 Job Description Matching
- 📊 Text Similarity
- 📈 Skill Match Score
- 🏆 Candidate Ranking
- 🥇 Top Candidate Recommendation
- 🔎 Candidate Search
- 🎯 Candidate Filtering
- 👤 Candidate Profile
- ✅ Matched Skills
- ❌ Missing Skills
- 📊 Candidate Comparison Charts
- 📥 CSV Ranking Export

## 🛠️ Technologies Used

- Python
- Streamlit
- Pandas
- NumPy
- Scikit-learn
- PyPDF2 / PDF processing
- NLP
- TF-IDF
- Cosine Similarity

## 📁 Project Structure

```text
AI-Resume-Screening-System/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│   ├── skills.csv
│   ├── job_descriptions/
│   └── resumes/
│
└── src/
    ├── pdf_parser.py
    ├── resume_parser.py
    ├── skill_extractor.py
    ├── ranking.py
    └── recommender.py