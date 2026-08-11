import os
import re
import tempfile
import streamlit as st

from src.pdf_parser import extract_text_from_pdf
from src.resume_parser import parse_resume
from src.skill_extractor import extract_skills
from src.ranking import rank_candidates
from src.recommender import add_recommendations


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Resume Screening System",
    page_icon="📄",
    layout="wide"
)


# ============================================================
# SESSION STATE
# ============================================================

if "ranking" not in st.session_state:
    st.session_state.ranking = None

if "ranking_job" not in st.session_state:
    st.session_state.ranking_job = None


# ============================================================
# PROJECT PATHS
# ============================================================

JOB_FOLDER = "data/job_descriptions"
RESUME_FOLDER = "data/resumes"
SKILLS_PATH = "data/skills.csv"


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_line(line):

    line = line.strip().lower()

    line = re.sub(
        r"[\:\|\-–—]+$",
        "",
        line
    )

    line = re.sub(
        r"[^a-z0-9+#& ]",
        "",
        line
    )

    line = re.sub(
        r"\s+",
        " ",
        line
    )

    return line.strip()


# ============================================================
# RESUME SECTION DETECTION
# ============================================================

def get_section_name(line):

    normalized = normalize_line(line)

    section_aliases = {

        "education": {
            "education",
            "educational background",
            "academic background",
            "academic qualification",
            "academic qualifications",
            "qualifications"
        },

        "experience": {
            "experience",
            "work experience",
            "professional experience",
            "work history",
            "employment history",
            "internship",
            "internships",
            "professional background"
        },

        "projects": {
            "projects",
            "project",
            "academic projects",
            "personal projects",
            "key projects",
            "major projects"
        },

        "certifications": {
            "certifications",
            "certification",
            "certificates",
            "certificate",
            "professional certifications",
            "certifications and achievements",
            "certifications achievements",
            "certifications & achievements"
        },

        "skills": {
            "skills",
            "technical skills",
            "technical skill",
            "skills and technologies",
            "technical expertise",
            "technologies",
            "core skills"
        },

        "summary": {
            "summary",
            "professional summary",
            "profile",
            "professional profile",
            "career objective",
            "objective",
            "about me"
        },

        "contact": {
            "contact",
            "contact information",
            "personal information"
        }
    }

    for section, aliases in section_aliases.items():

        if normalized in aliases:
            return section

    return None


# ============================================================
# EXTRACT RESUME SECTIONS
# ============================================================

def _as_clean_list(value):
    """Convert parser output into a clean list of non-empty strings."""
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    result = []
    try:
        for item in value:
            item = str(item).strip()
            item = re.sub(r"^[•●▪◦\-*]+\s*", "", item)
            item = re.sub(r"^\d+[\.)]\s*", "", item)
            if item:
                result.append(item)
    except TypeError:
        item = str(value).strip()
        if item:
            result.append(item)
    return result


def _clean_section_items(items, section):
    """Remove obvious cross-section contamination from parser output."""
    cleaned = []
    headings = {
        "education": {"education", "educational background", "academic background", "academic qualification", "academic qualifications", "qualifications"},
        "experience": {"experience", "work experience", "professional experience", "work history", "employment history", "internship", "internships", "professional background"},
        "projects": {"projects", "project", "academic projects", "personal projects", "key projects", "major projects"},
        "certifications": {"certifications", "certification", "certificates", "certificate", "professional certifications", "certifications and achievements", "certifications achievements", "certifications & achievements"},
        "skills": {"skills", "technical skills", "technical skill", "skills and technologies", "technical expertise", "technologies", "core skills"},
        "summary": {"summary", "professional summary", "profile", "professional profile", "career objective", "objective", "about me"},
    }
    summary_starts = (
        "motivated b.tech", "motivated b tech", "passionate about",
        "seeking internship", "active learner", "strong foundations in",
        "real-world problems", "real world problems"
    )
    for item in items:
        normalized = normalize_line(item)
        if not normalized or normalized in headings.get(section, set()):
            continue
        if section == "projects" and (normalized.startswith("certification") or normalized.startswith("certificate")):
            continue
        if section == "certifications" and normalized in headings["projects"]:
            continue
        if section in {"projects", "certifications"} and normalized.startswith(summary_starts):
            continue
        cleaned.append(item.strip())
    return cleaned


def extract_resume_sections(text):
    """Use resume_parser.py as the source of truth for resume sections."""
    empty = {"education": "", "experience": "", "projects": "", "certifications": "", "skills": "", "summary": ""}
    if not text or not text.strip():
        return empty
    try:
        parsed = parse_resume(text)
    except Exception:
        parsed = {}
    if not isinstance(parsed, dict):
        parsed = {}
    projects = _clean_section_items(_as_clean_list(parsed.get("projects")), "projects")
    certifications = _clean_section_items(_as_clean_list(parsed.get("certifications")), "certifications")
    return {
        "education": str(parsed.get("education", "") or "").strip(),
        "experience": str(parsed.get("experience", "") or "").strip(),
        "projects": "\n".join(projects),
        "certifications": "\n".join(certifications),
        "skills": str(parsed.get("skills", "") or "").strip(),
        "summary": str(parsed.get("summary", "") or "").strip(),
    }


# ============================================================
# EMAIL FALLBACK
# ============================================================

def extract_email_fallback(text):

    if not text:
        return ""

    email_pattern = (
        r"[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    )

    match = re.search(
        email_pattern,
        text
    )

    if match:
        return match.group(0)

    return ""


# ============================================================
# NAME FALLBACK
# ============================================================

def extract_name_fallback(text):

    if not text:
        return ""

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # --------------------------------------------------------
    # First useful line
    # --------------------------------------------------------

    for line in lines[:10]:

        clean = line.strip()

        # Skip obvious labels
        if clean.lower().startswith(
            (
                "name:",
                "email:",
                "phone:",
                "mobile:",
                "address:"
            )
        ):
            continue

        # Skip lines containing email
        if "@" in clean:
            continue

        # Skip very long lines
        if len(clean) > 60:
            continue

        # Skip common headings
        if normalize_line(clean) in {
            "resume",
            "curriculum vitae",
            "cv",
            "professional summary",
            "summary",
            "profile"
        }:
            continue

        # Name usually contains alphabetic characters
        if re.search(
            r"[A-Za-z]",
            clean
        ):

            return clean

    return ""


# ============================================================
# DISPLAY SECTION LINES
# ============================================================

def display_section_lines(text):

    if not text:
        return

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        # Remove repeated bullets
        line = re.sub(
            r"^[•●▪◦\-*]+\s*",
            "",
            line
        )

        if line:

            st.write(
                f"• {line}"
            )


# ============================================================
# DISPLAY LIST
# ============================================================

def display_list(items):

    if not items:
        return False

    if isinstance(
        items,
        str
    ):

        if items.strip():

            display_section_lines(
                items
            )

            return True

        return False

    try:

        for item in items:

            item = str(item).strip()

            if item:

                st.write(
                    f"• {item}"
                )

        return True

    except Exception:

        return False


# ============================================================
# HEADER
# ============================================================

st.title(
    "📄 AI Resume Screening & Candidate Recommendation System"
)

st.write(
    "An NLP-powered recruitment system for resume analysis, "
    "skill extraction, candidate ranking, and recommendation."
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "⚙️ Recruitment Settings"
)

st.sidebar.write(
    "Select the job description for candidate matching."
)


# ============================================================
# LOAD JOB DESCRIPTIONS
# ============================================================

if os.path.exists(
    JOB_FOLDER
):

    job_files = sorted(
        [
            file
            for file in os.listdir(
                JOB_FOLDER
            )
            if file.lower().endswith(".txt")
        ]
    )

else:

    job_files = []


# ============================================================
# JOB SELECTION
# ============================================================

if job_files:

    job_options = {}

    for file in job_files:

        display_name = (
            file
            .replace(
                ".txt",
                ""
            )
            .replace(
                "_",
                " "
            )
            .title()
        )

        job_options[
            display_name
        ] = file


    selected_job_name = st.sidebar.selectbox(
        "Select Job Description",
        list(
            job_options.keys()
        )
    )


    selected_job = job_options[
        selected_job_name
    ]


    st.sidebar.success(
        f"Selected: {selected_job_name}"
    )

else:

    selected_job_name = None

    selected_job = None

    st.sidebar.warning(
        "No job descriptions found."
    )


# ============================================================
# SECTION 1 — SINGLE RESUME ANALYSIS
# ============================================================

st.header(
    "📄 Resume Analysis"
)

st.write(
    "Upload one resume to analyze the candidate's "
    "information and detected skills."
)


uploaded_file = st.file_uploader(
    "Upload Your Resume",
    type=["pdf"],
    key="single_resume"
)


# ============================================================
# PROCESS SINGLE RESUME
# ============================================================

if uploaded_file is not None:

    st.success(
        f"Uploaded: {uploaded_file.name}"
    )


    temp_pdf = os.path.join(
        tempfile.gettempdir(),
        "single_resume.pdf"
    )


    try:

        with open(
            temp_pdf,
            "wb"
        ) as file:

            file.write(
                uploaded_file.getbuffer()
            )


        extracted_text = (
            extract_text_from_pdf(
                temp_pdf
            )
        )


    except Exception as error:

        st.error(
            f"❌ PDF extraction error: {error}"
        )

        extracted_text = ""


    if extracted_text:

        st.success(
            "✅ Resume text extracted successfully!"
        )


        # ====================================================
        # PARSE RESUME
        # ====================================================

        try:

            resume_data = parse_resume(
                extracted_text
            )

        except Exception:

            resume_data = {}


        # ====================================================
        # ROBUST SECTION EXTRACTION
        # ====================================================

        resume_sections = (
            extract_resume_sections(
                extracted_text
            )
        )


        # ====================================================
        # NAME
        # ====================================================

        detected_name = (
            resume_data.get(
                "name",
                ""
            )
            or extract_name_fallback(
                extracted_text
            )
        )


        # ====================================================
        # EMAIL
        # ====================================================

        detected_email = (
            resume_data.get(
                "email",
                ""
            )
            or extract_email_fallback(
                extracted_text
            )
        )


        # ====================================================
        # CANDIDATE INFORMATION
        # ====================================================

        st.divider()

        st.subheader(
            "👤 Detected Candidate Information"
        )


        col1, col2 = st.columns(2)


        with col1:

            st.write(
                "**Name**"
            )

            st.write(
                detected_name
                if detected_name
                else "Not detected"
            )


        with col2:

            st.write(
                "**Email**"
            )

            st.write(
                detected_email
                if detected_email
                else "Not detected"
            )


        # ====================================================
        # EDUCATION
        # ====================================================

        st.subheader(
            "🎓 Education"
        )


        education_text = (
            resume_sections.get(
                "education",
                ""
            )
            or resume_data.get(
                "education",
                ""
            )
        )


        if education_text:

            st.write(
                education_text
            )

        else:

            st.write(
                "Not detected"
            )


        # ====================================================
        # SKILLS
        # ====================================================

        st.subheader(
            "🎯 AI Skill Extraction"
        )


        try:

            detected_skills = extract_skills(
                extracted_text,
                SKILLS_PATH
            )

        except Exception as error:

            detected_skills = []

            st.error(
                f"❌ Skill extraction error: {error}"
            )


        if detected_skills:

            st.success(
                f"✅ {len(detected_skills)} skills detected"
            )


            skill_columns = st.columns(4)


            for index, skill in enumerate(
                detected_skills
            ):

                with skill_columns[
                    index % 4
                ]:

                    st.info(
                        f"✓ {skill.title()}"
                    )

        else:

            st.warning(
                "No skills detected."
            )


        # ====================================================
        # EXPERIENCE
        # ====================================================

        st.subheader(
            "💼 Experience"
        )


        experience_text = (
            resume_sections.get(
                "experience",
                ""
            )
            or resume_data.get(
                "experience",
                ""
            )
        )


        if experience_text:

            st.write(
                experience_text
            )

        else:

            st.write(
                "Not detected"
            )


        # ====================================================
        # PROJECTS
        # ====================================================

        st.subheader(
            "🚀 Projects"
        )


        projects = _clean_section_items(
            _as_clean_list(resume_data.get("projects")),
            "projects",
        )

        if projects:
            display_list(projects)
        else:
            st.write("No projects detected.")


        # ====================================================
        # CERTIFICATIONS
        # ====================================================

        st.subheader(
            "🏆 Certifications"
        )


        certifications = _clean_section_items(
            _as_clean_list(resume_data.get("certifications")),
            "certifications",
        )

        if certifications:
            display_list(certifications)
        else:
            st.write("No certifications detected.")


        # ====================================================
        # RAW TEXT
        # ====================================================

        with st.expander(
            "📋 View Extracted Resume Text"
        ):

            st.text_area(
                "Resume Content",
                extracted_text,
                height=450
            )


    else:

        st.error(
            "❌ No readable text was found in this PDF."
        )


# ============================================================
# SECTION 2 — CANDIDATE SCREENING
# ============================================================

st.divider()

st.header(
    "📤 Candidate Screening"
)

st.write(
    "Upload multiple candidate resumes directly "
    "from the application. You do not need to "
    "copy them into data/resumes."
)


candidate_files = st.file_uploader(
    "Upload Candidate Resumes",
    type=["pdf"],
    accept_multiple_files=True,
    key="candidate_uploads"
)


if candidate_files:

    st.success(
        f"✅ {len(candidate_files)} candidate resume(s) uploaded."
    )


    for candidate_file in candidate_files:

        st.write(
            f"📄 {candidate_file.name}"
        )


# ============================================================
# RANK UPLOADED CANDIDATES
# ============================================================

if candidate_files and selected_job:

    st.divider()

    st.subheader(
        "🚀 Candidate Ranking"
    )


    st.write(
        f"Selected Job: **{selected_job_name}**"
    )


    if st.button(
        "🚀 Rank Uploaded Candidates",
        type="primary",
        use_container_width=True
    ):

        temp_folder = tempfile.mkdtemp(
            prefix="resume_screening_"
        )


        # ----------------------------------------------------
        # SAVE PDFs
        # ----------------------------------------------------

        for candidate_file in candidate_files:

            filename = os.path.basename(
                candidate_file.name
            )


            file_path = os.path.join(
                temp_folder,
                filename
            )


            with open(
                file_path,
                "wb"
            ) as file:

                file.write(
                    candidate_file.getbuffer()
                )


        # ----------------------------------------------------
        # JOB PATH
        # ----------------------------------------------------

        job_path = os.path.join(
            JOB_FOLDER,
            selected_job
        )


        # ----------------------------------------------------
        # RANK
        # ----------------------------------------------------

        with st.spinner(
            "🔍 Analyzing candidate resumes..."
        ):

            try:

                ranking_result = rank_candidates(
                    temp_folder,
                    job_path,
                    SKILLS_PATH
                )


                ranking_result = (
                    add_recommendations(
                        ranking_result
                    )
                )


                # ------------------------------------------------
                # SAVE TO SESSION
                # ------------------------------------------------

                st.session_state.ranking = (
                    ranking_result
                )


                st.session_state.ranking_job = (
                    selected_job
                )


            except Exception as error:

                st.error(
                    f"❌ Ranking error: {error}"
                )


                st.session_state.ranking = None


# ============================================================
# GET RANKING
# ============================================================

ranking = (
    st.session_state.ranking
)


# ============================================================
# RANKING OUTPUT
# ============================================================

if (
    ranking is not None
    and not ranking.empty
):

    st.success(
        f"✅ {len(ranking)} candidates analyzed successfully!"
    )


    # ========================================================
    # DASHBOARD
    # ========================================================

    st.divider()

    st.subheader(
        "📊 Recruiter Dashboard"
    )


    total_candidates = len(
        ranking
    )


    best_candidate = ranking.iloc[0]


    best_score = float(
        best_candidate[
            "Final Score"
        ]
    )


    average_score = float(
        ranking[
            "Final Score"
        ].mean()
    )


    average_skill = float(
        ranking[
            "Skill Match"
        ].mean()
    )


    c1, c2, c3, c4 = st.columns(4)


    with c1:

        st.metric(
            "👥 Candidates",
            total_candidates
        )


    with c2:

        st.metric(
            "🏆 Best Score",
            f"{best_score:.2f}%"
        )


    with c3:

        st.metric(
            "📊 Average Score",
            f"{average_score:.2f}%"
        )


    with c4:

        st.metric(
            "🎯 Avg Skill Match",
            f"{average_skill:.2f}%"
        )


    st.info(
        f"🏆 Current top candidate: "
        f"**{best_candidate['Candidate']}**"
    )


    # ========================================================
    # TOP 3
    # ========================================================

    st.divider()

    st.subheader(
        "🏆 Top 3 Recommended Candidates"
    )


    top_candidates = ranking.head(
        min(
            3,
            len(ranking)
        )
    )


    for _, candidate in (
        top_candidates.iterrows()
    ):

        rank = int(
            candidate["Rank"]
        )


        if rank == 1:

            icon = "🥇"

        elif rank == 2:

            icon = "🥈"

        else:

            icon = "🥉"


        with st.container(
            border=True
        ):

            st.markdown(
                f"### {icon} Rank {rank} — "
                f"{candidate['Candidate']}"
            )


            a, b, c = st.columns(3)


            with a:

                st.metric(
                    "Text Similarity",
                    f"{float(candidate['Text Similarity']):.2f}%"
                )


            with b:

                st.metric(
                    "Skill Match",
                    f"{float(candidate['Skill Match']):.2f}%"
                )


            with c:

                st.metric(
                    "Final Score",
                    f"{float(candidate['Final Score']):.2f}%"
                )


            recommendation = str(
                candidate.get(
                    "Recommendation",
                    "Not Recommended"
                )
            )


            if recommendation in [
                "Highly Recommended",
                "Recommended"
            ]:

                st.success(
                    f"🟢 {recommendation}"
                )

            elif recommendation == "Consider":

                st.warning(
                    f"🟡 {recommendation}"
                )

            else:

                st.error(
                    f"🔴 {recommendation}"
                )


    # ========================================================
    # COMPLETE RANKING
    # ========================================================

    st.divider()

    st.subheader(
        "📊 Complete Candidate Ranking"
    )


    ranking_columns = [
        "Rank",
        "Candidate",
        "Text Similarity",
        "Skill Match",
        "Final Score",
        "Recommendation"
    ]


    available_columns = [
        column
        for column in ranking_columns
        if column in ranking.columns
    ]


    st.dataframe(
        ranking[
            available_columns
        ],
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # SEARCH & FILTER
    # ========================================================

    st.divider()

    st.subheader(
        "🔎 Candidate Search & Filter"
    )


    f1, f2, f3 = st.columns(3)


    with f1:

        search_name = st.text_input(
            "🔎 Search Candidate",
            placeholder="Enter candidate name..."
        )


    with f2:

        minimum_score = st.slider(
            "📊 Minimum Final Score",
            min_value=0,
            max_value=100,
            value=0,
            step=5
        )


    with f3:

        recommendation_filter = st.selectbox(
            "🎯 Recommendation",
            [
                "All",
                "Highly Recommended",
                "Recommended",
                "Consider",
                "Not Recommended"
            ]
        )


    filtered_ranking = (
        ranking.copy()
    )


    # --------------------------------------------------------
    # NAME
    # --------------------------------------------------------

    if search_name.strip():

        filtered_ranking = (
            filtered_ranking[
                filtered_ranking[
                    "Candidate"
                ]
                .astype(str)
                .str.contains(
                    search_name.strip(),
                    case=False,
                    na=False
                )
            ]
        )


    # --------------------------------------------------------
    # SCORE
    # --------------------------------------------------------

    filtered_ranking = (
        filtered_ranking[
            filtered_ranking[
                "Final Score"
            ] >= minimum_score
        ]
    )


    # --------------------------------------------------------
    # RECOMMENDATION
    # --------------------------------------------------------

    if recommendation_filter != "All":

        filtered_ranking = (
            filtered_ranking[
                filtered_ranking[
                    "Recommendation"
                ]
                == recommendation_filter
            ]
        )


    filtered_ranking = (
        filtered_ranking
        .sort_values(
            by="Final Score",
            ascending=False
        )
    )


    st.write(
        f"Showing **{len(filtered_ranking)}** candidate(s)"
    )


    if filtered_ranking.empty:

        st.warning(
            "⚠️ No candidates match the selected filters."
        )

    else:

        st.dataframe(
            filtered_ranking[
                available_columns
            ],
            use_container_width=True,
            hide_index=True
        )


    # ========================================================
    # STEP 12 — CANDIDATE PROFILE
    # ========================================================

    st.divider()

    st.subheader(
        "👤 Candidate Profile"
    )


    candidate_names = (
        ranking[
            "Candidate"
        ]
        .astype(str)
        .tolist()
    )


    selected_candidate = st.selectbox(
        "Select Candidate",
        candidate_names,
        key="profile_candidate"
    )


    selected_rows = ranking[
        ranking[
            "Candidate"
        ]
        .astype(str)
        == selected_candidate
    ]


    if not selected_rows.empty:

        selected_row = (
            selected_rows.iloc[0]
        )


        # ====================================================
        # SCORE INFORMATION
        # ====================================================

        st.markdown(
            f"## 👤 {selected_candidate}"
        )


        p1, p2, p3 = st.columns(3)


        with p1:

            st.metric(
                "📝 Text Similarity",
                f"{float(selected_row['Text Similarity']):.2f}%"
            )


        with p2:

            st.metric(
                "🎯 Skill Match",
                f"{float(selected_row['Skill Match']):.2f}%"
            )


        with p3:

            st.metric(
                "⭐ Final Score",
                f"{float(selected_row['Final Score']):.2f}%"
            )


        # ====================================================
        # RECOMMENDATION
        # ====================================================

        recommendation = str(
            selected_row.get(
                "Recommendation",
                "Not Recommended"
            )
        )


        if recommendation in [
            "Highly Recommended",
            "Recommended"
        ]:

            st.success(
                f"🟢 {recommendation}"
            )

        elif recommendation == "Consider":

            st.warning(
                f"🟡 {recommendation}"
            )

        else:

            st.error(
                f"🔴 {recommendation}"
            )


        # ====================================================
        # MATCHED SKILLS
        # ====================================================

        st.markdown(
            "### ✅ Matched Skills"
        )


        matched_skills = selected_row.get(
            "Matched Skills",
            ""
        )


        if (
            matched_skills
            and str(
                matched_skills
            ).strip()
        ):

            st.success(
                str(
                    matched_skills
                )
            )

        else:

            st.write(
                "No matched skills available."
            )


        # ====================================================
        # MISSING SKILLS
        # ====================================================

        st.markdown(
            "### ❌ Missing Skills"
        )


        missing_skills = selected_row.get(
            "Missing Skills",
            ""
        )


        if (
            missing_skills
            and str(
                missing_skills
            ).strip()
        ):

            st.warning(
                str(
                    missing_skills
                )
            )

        else:

            st.success(
                "No required skills missing."
            )


        # ====================================================
        # FIND SELECTED PDF
        # ====================================================

        selected_pdf = None


        if candidate_files:

            for candidate_file in candidate_files:

                if (
                    candidate_file.name
                    == selected_candidate
                ):

                    selected_pdf = candidate_file

                    break


        # ====================================================
        # FULL CANDIDATE INFORMATION
        # ====================================================

        st.markdown(
            "### 📄 Full Candidate Information"
        )


        if selected_pdf is not None:

            profile_pdf_path = os.path.join(
                tempfile.gettempdir(),
                "candidate_profile.pdf"
            )


            try:

                # --------------------------------------------
                # SAVE PDF
                # --------------------------------------------

                with open(
                    profile_pdf_path,
                    "wb"
                ) as file:

                    file.write(
                        selected_pdf.getbuffer()
                    )


                # --------------------------------------------
                # EXTRACT TEXT
                # --------------------------------------------

                profile_text = (
                    extract_text_from_pdf(
                        profile_pdf_path
                    )
                )


                if not profile_text:

                    st.error(
                        "❌ No readable text was found "
                        "in this candidate PDF."
                    )

                else:

                    # ----------------------------------------
                    # PARSE
                    # ----------------------------------------

                    try:

                        profile_data = parse_resume(
                            profile_text
                        )

                    except Exception:

                        profile_data = {}


                    # ----------------------------------------
                    # SECTION EXTRACTION
                    # ----------------------------------------

                    profile_sections = (
                        extract_resume_sections(
                            profile_text
                        )
                    )


                    # ----------------------------------------
                    # NAME
                    # ----------------------------------------

                    profile_name = (
                        profile_data.get(
                            "name",
                            ""
                        )
                        or extract_name_fallback(
                            profile_text
                        )
                    )


                    # ----------------------------------------
                    # EMAIL
                    # ----------------------------------------

                    profile_email = (
                        profile_data.get(
                            "email",
                            ""
                        )
                        or extract_email_fallback(
                            profile_text
                        )
                    )


                    # ========================================
                    # NAME + EMAIL
                    # ========================================

                    info1, info2 = st.columns(2)


                    with info1:

                        st.write(
                            "**Name**"
                        )

                        st.write(
                            profile_name
                            if profile_name
                            else "Not detected"
                        )


                    with info2:

                        st.write(
                            "**Email**"
                        )

                        st.write(
                            profile_email
                            if profile_email
                            else "Not detected"
                        )


                    # ========================================
                    # EDUCATION
                    # ========================================

                    st.markdown(
                        "### 🎓 Education"
                    )


                    education_text = (
                        profile_sections.get(
                            "education",
                            ""
                        )
                    )


                    if not education_text:

                        education_text = (
                            profile_data.get(
                                "education",
                                ""
                            )
                        )


                    if education_text:

                        st.write(
                            education_text
                        )

                    else:

                        st.write(
                            "Not detected"
                        )


                    # ========================================
                    # EXPERIENCE
                    # ========================================

                    st.markdown(
                        "### 💼 Experience"
                    )


                    experience_text = (
                        profile_sections.get(
                            "experience",
                            ""
                        )
                    )


                    if not experience_text:

                        experience_text = (
                            profile_data.get(
                                "experience",
                                ""
                            )
                        )


                    if experience_text:

                        st.write(
                            experience_text
                        )

                    else:

                        st.write(
                            "Not detected"
                        )


                    # ========================================
                    # PROJECTS
                    # ========================================

                    st.markdown(
                        "### 🚀 Projects"
                    )


                    projects = _clean_section_items(
                        _as_clean_list(profile_data.get("projects")),
                        "projects",
                    )

                    if projects:
                        display_list(projects)
                    else:
                        st.write("No projects detected.")


                    # ========================================
                    # CERTIFICATIONS
                    # ========================================

                    st.markdown(
                        "### 🏆 Certifications"
                    )


                    certifications = _clean_section_items(
                        _as_clean_list(profile_data.get("certifications")),
                        "certifications",
                    )

                    if certifications:
                        display_list(certifications)
                    else:
                        st.write("No certifications detected.")


                    # ========================================
                    # FULL RESUME TEXT
                    # ========================================

                    with st.expander(
                        "📋 View Candidate Resume Text"
                    ):

                        st.text_area(
                            "Resume Content",
                            profile_text,
                            height=450,
                            key="candidate_resume_text"
                        )


            except Exception as error:

                st.error(
                    f"❌ Could not load candidate profile: "
                    f"{error}"
                )

        else:

            st.info(
                "Upload the candidate PDF in "
                "'Candidate Screening' to view "
                "the complete candidate profile."
            )


    # ========================================================
    # COMPARISON CHARTS
    # ========================================================

    st.divider()

    st.subheader(
        "📊 Candidate Comparison Dashboard"
    )


    st.write(
        "### 🏆 Final Score Comparison"
    )


    final_chart = (
        ranking[
            [
                "Candidate",
                "Final Score"
            ]
        ]
        .set_index(
            "Candidate"
        )
    )


    st.bar_chart(
        final_chart
    )


    st.write(
        "### 🎯 Skill Match Comparison"
    )


    skill_chart = (
        ranking[
            [
                "Candidate",
                "Skill Match"
            ]
        ]
        .set_index(
            "Candidate"
        )
    )


    st.bar_chart(
        skill_chart
    )


    st.write(
        "### 📝 Text Similarity Comparison"
    )


    similarity_chart = (
        ranking[
            [
                "Candidate",
                "Text Similarity"
            ]
        ]
        .set_index(
            "Candidate"
        )
    )


    st.bar_chart(
        similarity_chart
    )


    # ========================================================
    # BEST CANDIDATE
    # ========================================================

    st.divider()

    st.subheader(
        "💡 Candidate Recommendation Explanation"
    )


    best = ranking.iloc[0]


    best_name = best[
        "Candidate"
    ]


    best_final = float(
        best[
            "Final Score"
        ]
    )


    best_skill = float(
        best[
            "Skill Match"
        ]
    )


    best_text = float(
        best[
            "Text Similarity"
        ]
    )


    st.success(
        f"🏆 Best Candidate: **{best_name}**"
    )


    b1, b2, b3 = st.columns(3)


    with b1:

        st.metric(
            "Final Score",
            f"{best_final:.2f}%"
        )


    with b2:

        st.metric(
            "Skill Match",
            f"{best_skill:.2f}%"
        )


    with b3:

        st.metric(
            "Text Similarity",
            f"{best_text:.2f}%"
        )


    st.markdown(
        "### 🔍 Why is this candidate ranked #1?"
    )


    if best_skill >= 80:

        st.write(
            "• Strong match with the required job skills."
        )

    elif best_skill >= 60:

        st.write(
            "• Good match with the required job skills."
        )

    else:

        st.write(
            "• Limited match with the required job skills."
        )


    if best_text >= 70:

        st.write(
            "• Resume content is highly similar "
            "to the selected job description."
        )

    elif best_text >= 40:

        st.write(
            "• Resume has moderate similarity "
            "to the selected job description."
        )

    else:

        st.write(
            "• Resume has relatively low similarity "
            "to the selected job description."
        )


    # ========================================================
    # CSV EXPORT
    # ========================================================

    st.divider()

    st.subheader(
        "📥 Export Results"
    )


    csv_data = ranking.to_csv(
        index=False
    )


    st.download_button(
        label="📥 Download Candidate Ranking CSV",
        data=csv_data,
        file_name="candidate_ranking.csv",
        mime="text/csv",
        use_container_width=True
    )


# ============================================================
# CANDIDATES UPLOADED BUT NO JOB
# ============================================================

elif (
    candidate_files
    and not selected_job
):

    st.warning(
        "⚠️ Please select a Job Description "
        "before ranking candidates."
    )


# ============================================================
# EXISTING RESUMES
# ============================================================

st.divider()


with st.expander(
    "📁 Rank Existing Resumes from data/resumes"
):

    st.write(
        "Use this option to rank resumes already "
        "stored inside data/resumes/."
    )


    if selected_job:

        if st.button(
            "📊 Rank Existing Candidates",
            use_container_width=True
        ):

            job_path = os.path.join(
                JOB_FOLDER,
                selected_job
            )


            try:

                with st.spinner(
                    "🔍 Analyzing existing resumes..."
                ):

                    existing_ranking = (
                        rank_candidates(
                            RESUME_FOLDER,
                            job_path,
                            SKILLS_PATH
                        )
                    )


                    existing_ranking = (
                        add_recommendations(
                            existing_ranking
                        )
                    )


                    st.session_state.ranking = (
                        existing_ranking
                    )


                    st.session_state.ranking_job = (
                        selected_job
                    )


                    st.rerun()


            except Exception as error:

                st.error(
                    f"❌ Ranking error: {error}"
                )


# ============================================================
# JOB DESCRIPTION PREVIEW
# ============================================================

if selected_job:

    st.divider()


    with st.expander(
        "📋 View Selected Job Description"
    ):

        job_path = os.path.join(
            JOB_FOLDER,
            selected_job
        )


        try:

            with open(
                job_path,
                "r",
                encoding="utf-8"
            ) as file:

                job_text = file.read()


            st.text_area(
                "Job Description",
                job_text,
                height=300
            )


        except Exception as error:

            st.error(
                f"❌ Could not load job description: "
                f"{error}"
            )


# ============================================================
# PROJECT STATUS
# ============================================================

st.divider()


st.info(
    "🚧 Current Version: Direct PDF resume upload, "
    "resume parsing, robust section extraction, "
    "AI skill extraction, job matching, TF-IDF similarity, "
    "skill matching, candidate ranking, Top-3 recommendation, "
    "search and filtering, candidate profile, matched and "
    "missing skills, comparison charts, recommendation "
    "explanation, and CSV export."
)