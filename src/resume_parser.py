import re


# ============================================================
# BASIC CLEANING
# ============================================================

def clean_line(line):
    """Clean one extracted PDF line."""

    if not line:
        return ""

    line = line.replace("\u00a0", " ")

    # Normalize whitespace
    line = re.sub(r"\s+", " ", line).strip()

    return line


def get_clean_lines(text):
    """Return non-empty cleaned lines."""

    if not text:
        return []

    return [
        clean_line(line)
        for line in text.splitlines()
        if clean_line(line)
    ]


# ============================================================
# SECTION HEADINGS
# ============================================================

SECTION_HEADINGS = {
    "professional summary",
    "summary",
    "profile",
    "objective",

    "education",
    "academic background",
    "educational background",
    "academic qualifications",
    "qualification",
    "qualifications",

    "technical skills",
    "technical skill",
    "skills",
    "key skills",
    "core skills",

    "experience",
    "work experience",
    "professional experience",
    "employment history",
    "work history",

    "internship",
    "internships",
    "internship experience",
    "virtual internships",

    "projects",
    "project",
    "academic projects",
    "personal projects",
    "project experience",

    "certifications",
    "certification",
    "certificates",
    "licenses and certifications",

    "achievements",
    "accomplishments",
    "awards",

    "languages",
    "interests",
    "contact",
    "references",
}


def normalize_heading(line):
    """Normalize a possible section heading."""

    if not line:
        return ""

    line = clean_line(line)

    line = re.sub(
        r"^[•●▪◦\-\*]+\s*",
        "",
        line
    )

    line = re.sub(
        r":\s*$",
        "",
        line
    )

    return line.lower().strip()


def is_section_heading(line):
    """Return True if line is a known section heading."""

    return normalize_heading(line) in SECTION_HEADINGS


# ============================================================
# PDF CHARACTER SPACING
# ============================================================

def is_spaced_character_line(line):
    """
    Detect PDF extraction such as:

    M O H D N A V E D A B B A S
    """

    words = line.split()

    if len(words) < 6:
        return False

    single_letters = [
        word
        for word in words
        if len(word) == 1 and word.isalpha()
    ]

    return (
        len(single_letters) >= 6
        and len(single_letters) / len(words) >= 0.70
    )


def compact_spaced_line(line):
    """Remove artificial spaces between PDF characters."""

    if not is_spaced_character_line(line):
        return line

    return "".join(line.split())


# ============================================================
# NAME VALIDATION
# ============================================================

NAME_REJECT_WORDS = {
    "resume",
    "curriculum",
    "vitae",
    "profile",
    "summary",
    "objective",
    "education",
    "experience",
    "projects",
    "project",
    "skills",
    "technical",
    "certifications",
    "certification",
    "developer",
    "engineer",
    "enthusiast",
    "student",
    "analyst",
    "professional",
    "programmer",
    "intern",
    "internship",
    "software",
    "development",
    "machine",
    "learning",
    "python",
    "data",
    "science",
    "computer",
}


def valid_name_format(name):
    """Check whether text looks like a person's name."""

    if not name:
        return False

    name = clean_line(name)

    if len(name) < 3 or len(name) > 70:
        return False

    if "@" in name:
        return False

    if "|" in name:
        return False

    if any(char.isdigit() for char in name):
        return False

    words = name.split()

    if not 2 <= len(words) <= 5:
        return False

    for word in words:

        if not re.fullmatch(
            r"[A-Za-z][A-Za-z.'-]*",
            word
        ):
            return False

    if any(
        word.lower() in NAME_REJECT_WORDS
        for word in words
    ):
        return False

    return True


# ============================================================
# RECOVER SPACED NAME
# ============================================================

COMMON_NAME_WORDS = {
    "aarav",
    "aaryan",
    "aditya",
    "aman",
    "amit",
    "ankit",
    "arjun",
    "ashish",
    "ayush",
    "deepak",
    "gaurav",
    "harsh",
    "imran",
    "karan",
    "mohd",
    "mohammed",
    "mohammad",
    "naveen",
    "naved",
    "neeraj",
    "nikhil",
    "rahul",
    "raj",
    "rohan",
    "sachin",
    "sahil",
    "sameer",
    "shubham",
    "sumit",
    "varun",
    "vishal",
    "yash",

    # Important for your resume
    "abbas",
}


def recover_spaced_name(compact):
    """
    Recover a name from a PDF string such as:

        MOHDNAVEDABBAS

    ->

        MOHD NAVED ABBAS
    """

    if not compact:
        return ""

    compact = re.sub(
        r"[^A-Za-z]",
        "",
        compact
    ).lower()

    if not compact:
        return ""

    # --------------------------------------------------------
    # Dynamic word segmentation using known name words
    # --------------------------------------------------------

    memo = {}

    def segment(value):

        if value == "":
            return []

        if value in memo:
            return memo[value]

        solutions = []

        for word in COMMON_NAME_WORDS:

            if value.startswith(word):

                remainder = value[len(word):]

                result = segment(remainder)

                if result is not None:

                    solutions.append(
                        [word] + result
                    )

        if not solutions:

            memo[value] = None
            return None

        # Prefer fewer, longer words
        solutions.sort(
            key=lambda x: (
                len(x),
                -sum(len(w) for w in x)
            )
        )

        memo[value] = solutions[0]

        return solutions[0]

    result = segment(compact)

    if not result:
        return ""

    if not 2 <= len(result) <= 4:
        return ""

    name = " ".join(result).upper()

    if valid_name_format(name):
        return name

    return ""


# ============================================================
# NAME EXTRACTION
# ============================================================

def extract_name(text):
    """
    Extract candidate name.

    Handles:

    Name: John Smith

    JOHN SMITH

    M O H D N A V E D A B B A S

    MOHDNAVEDABBAS
    """

    lines = get_clean_lines(text)

    if not lines:
        return ""

    # --------------------------------------------------------
    # 1. Explicit Name: field
    # --------------------------------------------------------

    for line in lines[:20]:

        match = re.match(
            r"^(?:name|candidate name)"
            r"\s*[:\-]\s*(.+)$",
            line,
            re.IGNORECASE
        )

        if match:

            candidate = clean_line(
                match.group(1)
            )

            if valid_name_format(candidate):
                return candidate

    # --------------------------------------------------------
    # 2. Look specifically for PDF spaced name
    # --------------------------------------------------------

    for line in lines[:30]:

        if is_spaced_character_line(line):

            compact = compact_spaced_line(
                line
            )

            recovered = recover_spaced_name(
                compact
            )

            if recovered:
                return recovered

    # --------------------------------------------------------
    # 3. Look for compact uppercase name
    # --------------------------------------------------------

    for line in lines[:30]:

        compact = re.sub(
            r"[^A-Za-z]",
            "",
            line
        )

        if (
            line.isupper()
            and valid_name_format(line)
        ):
            return line

        recovered = recover_spaced_name(
            compact
        )

        if recovered:
            return recovered

    # --------------------------------------------------------
    # 4. Conservative fallback
    #
    # DO NOT simply return the first line.
    # --------------------------------------------------------

    for line in lines[:15]:

        if "|" in line:
            continue

        if "@" in line:
            continue

        if is_section_heading(line):
            continue

        if valid_name_format(line):

            # Prefer uppercase / title-case names
            words = line.split()

            if all(
                word[0].isupper()
                for word in words
                if word
            ):
                return line

    return ""


# ============================================================
# EMAIL
# ============================================================

def extract_email(text):
    """Extract email address."""

    if not text:
        return ""

    pattern = (
        r"\b[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+"
        r"\.[A-Za-z]{2,}\b"
    )

    match = re.search(
        pattern,
        text
    )

    if match:
        return match.group(0)

    return ""


# ============================================================
# SECTION FINDING
# ============================================================

def find_heading_indexes(lines, section_names):
    """
    Find all positions of requested section headings.
    """

    wanted = {
        name.lower()
        for name in section_names
    }

    indexes = []

    for index, line in enumerate(lines):

        if normalize_heading(line) in wanted:
            indexes.append(index)

    return indexes


def get_section(lines, section_names):
    """
    Standard section extraction.

    Used when the PDF has normal section ordering.
    """

    indexes = find_heading_indexes(
        lines,
        section_names
    )

    if not indexes:
        return []

    start = indexes[0] + 1

    section_lines = []

    for line in lines[start:]:

        if is_section_heading(line):
            break

        if line.strip():
            section_lines.append(line)

    return section_lines


# ============================================================
# EDUCATION
# ============================================================

def extract_education(text):
    """
    Extract education information.

    Also handles PDFs where EDUCATION is present as a heading
    but the actual education details appear elsewhere in the
    extracted text.
    """

    lines = get_clean_lines(text)

    # --------------------------------------------------------
    # Normal section
    # --------------------------------------------------------

    education_lines = get_section(
        lines,
        [
            "Education",
            "Academic Background",
            "Educational Background",
            "Academic Qualifications",
            "Qualification",
            "Qualifications",
        ]
    )

    if education_lines:
        return "\n".join(
            education_lines
        )

    # --------------------------------------------------------
    # Fallback: search complete extracted text
    # for education keywords.
    # --------------------------------------------------------

    education_matches = []

    education_patterns = [
        r"B\.?\s*Tech[^,\n]*",
        r"B\.?\s*E\.?[^,\n]*",
        r"M\.?\s*Tech[^,\n]*",
        r"M\.?\s*E\.?[^,\n]*",
        r"BCA[^,\n]*",
        r"MCA[^,\n]*",
        r"BSc[^,\n]*",
        r"MSc[^,\n]*",
        r"Computer Science[^,\n]*",
        r"Meerut Institute of Technology[^,\n]*",
    ]

    for pattern in education_patterns:

        matches = re.findall(
            pattern,
            text,
            re.IGNORECASE
        )

        for match in matches:

            match = clean_line(match)

            if match and match not in education_matches:
                education_matches.append(match)

    # --------------------------------------------------------
    # Add nearby lines containing degree information
    # --------------------------------------------------------

    for index, line in enumerate(lines):

        lower = line.lower()

        if (
            "b.tech" in lower
            or "btech" in lower
            or "computer science" in lower
            or "institute of technology" in lower
        ):

            for candidate in lines[
                max(0, index - 1):
                min(len(lines), index + 3)
            ]:

                if candidate not in education_matches:
                    education_matches.append(
                        candidate
                    )

    # Keep only useful lines
    useful = []

    for line in education_matches:

        lower = line.lower()

        if any(
            keyword in lower
            for keyword in [
                "b.tech",
                "btech",
                "computer science",
                "institute",
                "college",
                "university",
                "cgpa",
                "gpa",
                "2023",
                "2024",
                "2025",
                "2026",
                "2027",
            ]
        ):

            if line not in useful:
                useful.append(line)

    return "\n".join(useful[:10])


# ============================================================
# EXPERIENCE
# ============================================================

def extract_experience(text):
    """Extract professional experience."""

    lines = get_clean_lines(text)

    experience_lines = get_section(
        lines,
        [
            "Experience",
            "Work Experience",
            "Professional Experience",
            "Employment History",
            "Work History",
        ]
    )

    return "\n".join(
        experience_lines
    )


# ============================================================
# INTERNSHIPS
# ============================================================

def extract_internships(text):
    """Extract internship information."""

    lines = get_clean_lines(text)

    internship_lines = get_section(
        lines,
        [
            "Internship",
            "Internships",
            "Internship Experience",
            "Virtual Internships",
        ]
    )

    if internship_lines:
        return "\n".join(
            internship_lines
        )

    # Fallback: search for internship content
    results = []

    for index, line in enumerate(lines):

        if "internship" in line.lower():

            results.append(line)

            # Include next few lines
            for extra in lines[
                index + 1:index + 4
            ]:

                if not is_section_heading(extra):
                    results.append(extra)

    return "\n".join(
        dict.fromkeys(results)
    )


# ============================================================
# PROJECTS
# ============================================================

def extract_projects(text):
    """Extract projects."""

    lines = get_clean_lines(text)

    project_lines = get_section(
        lines,
        [
            "Projects",
            "Project",
            "Academic Projects",
            "Personal Projects",
            "Project Experience",
        ]
    )

    projects = []

    for line in project_lines:

        line = re.sub(
            r"^[•●▪◦\-\*]\s*",
            "",
            line
        ).strip()

        if line:
            projects.append(line)

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    if not projects:

        project_keywords = [
            "restaurant website",
            "food chart",
            "student performance",
            "house price prediction",
            "customer churn",
            "sentiment analysis",
        ]

        for line in lines:

            lower = line.lower()

            if any(
                keyword in lower
                for keyword in project_keywords
            ):

                if line not in projects:
                    projects.append(line)

    return projects


# ============================================================
# CERTIFICATIONS
# ============================================================

def extract_certifications(text):
    """Extract certifications."""

    lines = get_clean_lines(text)

    certification_lines = get_section(
        lines,
        [
            "Certifications",
            "Certification",
            "Certificates",
            "Licenses and Certifications",
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

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    if not certifications:

        certification_keywords = [
            "certification",
            "certificate",
            "skills passport",
            "skillsbuild",
            "hp life",
            "cisco",
            "tcs ion",
            "google for developers",
        ]

        for line in lines:

            lower = line.lower()

            if any(
                keyword in lower
                for keyword in certification_keywords
            ):

                if line not in certifications:
                    certifications.append(line)

    return certifications


# ============================================================
# SKILLS
# ============================================================

def extract_skills_section(text):
    """Extract technical skills as raw text."""

    lines = get_clean_lines(text)

    skill_lines = get_section(
        lines,
        [
            "Technical Skills",
            "Technical Skill",
            "Skills",
            "Key Skills",
            "Core Skills",
        ]
    )

    return "\n".join(
        skill_lines
    )


# ============================================================
# ACHIEVEMENTS
# ============================================================

def extract_achievements(text):
    """Extract achievements."""

    lines = get_clean_lines(text)

    achievement_lines = get_section(
        lines,
        [
            "Achievements",
            "Accomplishments",
            "Awards",
        ]
    )

    return "\n".join(
        achievement_lines
    )


# ============================================================
# ROBUST SECTION EXTRACTION
# ============================================================

def extract_resume_sections(text):
    """
    Extract major resume sections.

    """

    sections = {
        "education": "",
        "experience": "",
        "internships": "",
        "projects": "",
        "certifications": "",
        "skills": "",
        "achievements": "",
    }

    if not text:
        return sections

    lines = get_clean_lines(text)

    section_names = {

        "education": [
            "education",
            "academic background",
            "educational background",
            "academic qualifications",
            "qualification",
            "qualifications",
        ],

        "experience": [
            "experience",
            "work experience",
            "professional experience",
            "employment history",
            "work history",
        ],

        "internships": [
            "internship",
            "internships",
            "internship experience",
            "virtual internships",
        ],

        "projects": [
            "projects",
            "project",
            "academic projects",
            "personal projects",
            "project experience",
        ],

        "certifications": [
            "certifications",
            "certification",
            "certificates",
            "licenses and certifications",
        ],

        "skills": [
            "technical skills",
            "technical skill",
            "skills",
            "key skills",
            "core skills",
        ],

        "achievements": [
            "achievements",
            "accomplishments",
            "awards",
        ],
    }

    heading_lookup = {}

    for section, headings in section_names.items():

        for heading in headings:

            heading_lookup[
                heading.lower()
            ] = section

    current_section = None

    for line in lines:

        normalized = normalize_heading(
            line
        )

        if normalized in heading_lookup:

            current_section = heading_lookup[
                normalized
            ]

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


# ============================================================
# MAIN PARSER
# ============================================================

def parse_resume(text):
    """
    Parse complete resume.

    This structure remains compatible with app.py.
    """

    if not text:

        return {
            "name": "",
            "email": "",
            "education": "",
            "skills": [],
            "experience": "",
            "projects": [],
            "certifications": [],
            "internships": "",
            "achievements": "",
        }

    return {
        "name": extract_name(text),

        "email": extract_email(text),

        "education": extract_education(text),

        # AI skill extraction is handled separately
        "skills": [],

        "experience": extract_experience(text),

        "projects": extract_projects(text),

        "certifications": extract_certifications(text),

        "internships": extract_internships(text),

        "achievements": extract_achievements(text),
    }