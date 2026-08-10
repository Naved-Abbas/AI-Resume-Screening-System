import re


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_line(line):
    """Clean one line of extracted PDF text."""

    line = line.replace("\u00a0", " ")
    line = re.sub(r"\s+", " ", line)
    return line.strip()


def is_section_heading(line):
    """Check whether a line is a resume section heading."""

    normalized = line.lower().strip()

    headings = {
        "professional summary",
        "summary",
        "education",
        "technical skills",
        "skills",
        "experience",
        "work experience",
        "projects",
        "certifications",
        "certificates",
        "achievements",
        "languages",
        "interests",
        "contact",
    }

    return normalized in headings


def get_section(lines, section_names):
    """
    Extract lines belonging to a particular resume section.
    """

    section_names = {
        name.lower()
        for name in section_names
    }

    start_index = None

    for i, line in enumerate(lines):

        if line.lower().strip() in section_names:

            start_index = i + 1
            break

    if start_index is None:

        return []

    section_lines = []

    for line in lines[start_index:]:

        if is_section_heading(line):

            break

        if line.strip():

            section_lines.append(
                line.strip()
            )

    return section_lines


# ============================================================
# NAME
# ============================================================

def extract_name(text):
    """
    Extract candidate name.

    For the user's resume, the name appears
    as the first non-empty line.
    """

    lines = [
        clean_line(line)
        for line in text.splitlines()
        if clean_line(line)
    ]

    if not lines:

        return ""

    # --------------------------------------------------------
    # First check explicit Name:
    # --------------------------------------------------------

    for line in lines[:10]:

        match = re.match(
            r"^(?:name)\s*[:\-]\s*(.+)$",
            line,
            re.IGNORECASE
        )

        if match:

            return match.group(1).strip()


    # --------------------------------------------------------
    # Otherwise use first line
    # --------------------------------------------------------

    first_line = lines[0]

    # Avoid using headings as name
    if not is_section_heading(first_line):

        return first_line

    return ""


# ============================================================
# EMAIL
# ============================================================

def extract_email(text):
    """Extract email address."""

    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"

    match = re.search(
        pattern,
        text
    )

    if match:

        return match.group(0)

    return ""


# ============================================================
# EDUCATION
# ============================================================

def extract_education(text):
    """Extract education section."""

    lines = [
        clean_line(line)
        for line in text.splitlines()
        if clean_line(line)
    ]

    education_lines = get_section(
        lines,
        [
            "Education"
        ]
    )

    return "\n".join(
        education_lines
    )


# ============================================================
# EXPERIENCE
# ============================================================

def extract_experience(text):
    """Extract experience section."""

    lines = [
        clean_line(line)
        for line in text.splitlines()
        if clean_line(line)
    ]

    experience_lines = get_section(
        lines,
        [
            "Experience",
            "Work Experience"
        ]
    )

    return "\n".join(
        experience_lines
    )


# ============================================================
# PROJECTS
# ============================================================

def extract_projects(text):
    """Extract projects section."""

    lines = [
        clean_line(line)
        for line in text.splitlines()
        if clean_line(line)
    ]

    project_lines = get_section(
        lines,
        [
            "Projects"
        ]
    )

    projects = []

    for line in project_lines:

        # Remove common bullet symbols
        line = re.sub(
            r"^[•●▪◦\-\*]\s*",
            "",
            line
        ).strip()

        if line:

            projects.append(line)

    return projects


# ============================================================
# CERTIFICATIONS
# ============================================================

def extract_certifications(text):
    """Extract certifications section."""

    lines = [
        clean_line(line)
        for line in text.splitlines()
        if clean_line(line)
    ]

    certification_lines = get_section(
        lines,
        [
            "Certifications",
            "Certificates"
        ]
    )

    certifications = []

    for line in certification_lines:

        line = re.sub(
            r"^[•●▪◦\-\*]\s*",
            "",
            line
        ).strip()

        if line:

            certifications.append(line)

    return certifications


# ============================================================
# SKILLS
# ============================================================

def extract_skills_section(text):
    """
    Extract the Technical Skills section as raw text.

    Actual AI skill extraction is handled by
    skill_extractor.py.
    """

    lines = [
        clean_line(line)
        for line in text.splitlines()
        if clean_line(line)
    ]

    skill_lines = get_section(
        lines,
        [
            "Technical Skills",
            "Skills"
        ]
    )

    return "\n".join(
        skill_lines
    )


# ============================================================
# MAIN RESUME PARSER
# ============================================================

def parse_resume(text):
    """
    Parse complete resume information.
    """

    resume_data = {

        "name": extract_name(text),

        "email": extract_email(text),

        "education": extract_education(text),

        "skills": [],

        "experience": extract_experience(text),

        "projects": extract_projects(text),

        "certifications": extract_certifications(text)

    }

    return resume_data

# ============================================================
# ROBUST SECTION EXTRACTION
# ============================================================

def extract_resume_sections(text):

    import re

    sections = {
        "education": "",
        "experience": "",
        "projects": "",
        "certifications": ""
    }

    if not text:
        return sections

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    current_section = None

    section_names = {
        "education": [
            "education",
            "academic background",
            "educational background"
        ],

        "experience": [
            "experience",
            "work experience",
            "professional experience",
            "internship",
            "internships"
        ],

        "projects": [
            "projects",
            "project",
            "academic projects",
            "personal projects"
        ],

        "certifications": [
            "certifications",
            "certification",
            "certificates",
            "certifications & achievements"
        ]
    }

    for line in lines:

        clean_line = re.sub(
            r"[^a-zA-Z& ]",
            "",
            line
        ).strip().lower()

        found_section = None

        for section, headings in section_names.items():

            for heading in headings:

                if clean_line == heading:
                    found_section = section
                    break

            if found_section:
                break

        if found_section:

            current_section = found_section
            continue

        if current_section:

            sections[current_section] += (
                line + "\n"
            )

    for section in sections:

        sections[section] = (
            sections[section]
            .strip()
        )

    return sections