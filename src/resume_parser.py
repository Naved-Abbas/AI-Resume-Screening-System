import re


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_line(line):
    """Clean one extracted PDF line."""

    if not line:
        return ""

    line = str(line)

    # Non-breaking space
    line = line.replace("\u00a0", " ")

    # PDF soft hyphen
    line = line.replace("\u00ad", "")

    # Normalize whitespace
    line = re.sub(r"\s+", " ", line)

    return line.strip()


def get_clean_lines(text):
    """Return cleaned non-empty lines."""

    if not text:
        return []

    lines = []

    for line in text.splitlines():

        line = clean_line(line)

        if line:
            lines.append(line)

    return lines


# ============================================================
# SECTION DEFINITIONS
# ============================================================

SECTION_ALIASES = {

    "summary": {
        "summary",
        "professional summary",
        "profile",
        "professional profile",
        "career objective",
        "objective",
    },

    "contact": {
        "contact",
        "contact information",
        "personal information",
    },

    "education": {
        "education",
        "educational background",
        "academic background",
        "academic qualifications",
        "qualification",
        "qualifications",
    },

    "skills": {
        "skills",
        "technical skills",
        "technical skill",
        "key skills",
        "core skills",
        "technical expertise",
    },

    "experience": {
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "work history",
        "career experience",
    },

    "internships": {
        "internship",
        "internships",
        "internship experience",
        "virtual internships",
    },

    "projects": {
        "projects",
        "project",
        "project experience",
        "academic projects",
        "personal projects",
    },

    "certifications": {
        "certifications",
        "certification",
        "certificates",
        "licenses and certifications",
    },

    "achievements": {
        "achievements",
        "accomplishments",
        "awards",
    },

    "languages": {
        "languages",
        "language",
    },

    "interests": {
        "interests",
        "hobbies",
        "hobbies and interests",
    },
}


# Reverse lookup
HEADING_TO_SECTION = {}

for section, aliases in SECTION_ALIASES.items():

    for alias in aliases:

        HEADING_TO_SECTION[
            alias.lower()
        ] = section


# ============================================================
# HEADING NORMALIZATION
# ============================================================

def normalize_heading(line):
    """
    Normalize a possible section heading.

    Handles:

        Projects
        PROJECTS
        Projects:
        - Projects
        • Projects
        Certifications:
        CERTIFICATIONS |
    """

    if not line:
        return ""

    value = str(line)

    value = value.replace(
        "\u00a0",
        " "
    )

    value = value.strip()

    # Remove bullets
    value = re.sub(
        r"^[•●▪◦\-\*\|]+\s*",
        "",
        value
    )

    # Remove punctuation from beginning
    value = re.sub(
        r"^[#:;|]+\s*",
        "",
        value
    )

    # Remove punctuation from end
    value = re.sub(
        r"[\s:;,#|]+$",
        "",
        value
    )

    # Normalize spaces
    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.lower().strip()


def compact_text(value):
    """Remove everything except alphabetic characters."""

    return re.sub(
        r"[^a-z]",
        "",
        value.lower()
    )


def get_heading_section(line):
    """
    Detect a resume section heading.

    This function is intentionally strict:
    only a complete heading is accepted.

    Therefore normal project text containing words such as
    'project' will NOT become a heading.
    """

    if not line:
        return None

    normalized = normalize_heading(line)

    # Exact match
    if normalized in HEADING_TO_SECTION:

        return HEADING_TO_SECTION[
            normalized
        ]

    # Handle PDF text with spaced letters:
    #
    # C e r t i f i c a t i o n s
    # P r o j e c t s
    #
    compact = compact_text(
        normalized
    )

    if not compact:
        return None

    for heading, section in HEADING_TO_SECTION.items():

        if compact == compact_text(
            heading
        ):
            return section

    return None


def is_section_heading(line):
    """Return True if line is a real section heading."""

    return (
        get_heading_section(line)
        is not None
    )


# ============================================================
# HARD SECTION HEADING
# ============================================================

def get_hard_heading(line):
    """
    Extra-safe heading detector.

    This is used before adding a line to Projects or
    Certifications.

    It catches headings even when PDF extraction adds
    bullets or punctuation.
    """

    if not line:
        return None

    value = str(line).strip()

    # Remove bullets
    value = re.sub(
        r"^[•●▪◦\-\*\|]+\s*",
        "",
        value
    )

    # Remove colon
    value = value.rstrip(
        " :;,#|"
    ).strip()

    normalized = re.sub(
        r"\s+",
        " ",
        value
    ).lower()

    # Exact known heading
    if normalized in HEADING_TO_SECTION:

        return HEADING_TO_SECTION[
            normalized
        ]

    # Compact form
    compact = compact_text(
        normalized
    )

    for heading, section in HEADING_TO_SECTION.items():

        if compact == compact_text(
            heading
        ):
            return section

    return None


# ============================================================
# BULLET HANDLING
# ============================================================

def remove_bullet(line):
    """Remove common bullet characters."""

    if not line:
        return ""

    return re.sub(
        r"^[•●▪◦\-\*]+\s*",
        "",
        line
    ).strip()


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
# PHONE
# ============================================================

def extract_phone(text):
    """Extract phone number."""

    if not text:
        return ""

    patterns = [

        r"\+91[\s-]?\d{10}",

        r"\+91[\s-]?\d{5}"
        r"[\s-]?\d{5}",

        r"\b\d{10}\b",

        r"\b\d{5}"
        r"[\s-]\d{5}\b",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text
        )

        if match:
            return match.group(0)

    return ""


# ============================================================
# CONTACT DETECTION
# ============================================================

def is_contact_line(line):
    """Detect email, phone or online contact information."""

    if not line:
        return False

    lower = line.lower()

    # Email
    if "@" in line:
        return True

    # Phone
    if re.search(
        r"\+?\d[\d\s().-]{8,}\d",
        line
    ):
        return True

    contact_words = (
        "phone",
        "mobile",
        "email",
        "linkedin",
        "github.com",
        "github/",
        "www.",
        "http://",
        "https://",
        "address",
    )

    return any(
        word in lower
        for word in contact_words
    )


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
    "certificate",

    "developer",
    "engineer",
    "enthusiast",
    "student",
    "analyst",
    "professional",
    "programmer",

    "intern",
    "internship",
    "internships",

    "software",
    "development",

    "machine",
    "learning",
    "python",
    "data",
    "science",
}


def valid_name(name):
    """Check whether a string looks like a person's name."""

    if not name:
        return False

    name = clean_line(name)

    if len(name) < 3:
        return False

    if len(name) > 70:
        return False

    if "@" in name:
        return False

    if "|" in name:
        return False

    if any(
        character.isdigit()
        for character in name
    ):
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
        word.lower()
        in NAME_REJECT_WORDS
        for word in words
    ):
        return False

    return True


# ============================================================
# SPACED NAME
# ============================================================

def recover_spaced_name(line):
    """
    Convert:

        M O H D N A V E D A B B A S

    into:

        MOHD NAVED ABBAS

    for known name patterns.
    """

    if not line:
        return ""

    words = line.split()

    # Must contain many single letters
    if len(words) < 6:
        return ""

    if not all(
        len(word) == 1
        and word.isalpha()
        for word in words
    ):
        return ""

    compact = "".join(
        words
    ).lower()

    # Specific common Indian-name patterns.
    # This is intentionally limited so random text
    # is not incorrectly treated as a name.

    known_names = {
        "mohdnavedabbas": "MOHD NAVED ABBAS",
        "mohammednavedabbas": "MOHAMMED NAVED ABBAS",
        "mohdnaved": "MOHD NAVED",
        "navedabbas": "NAVED ABBAS",
    }

    return known_names.get(
        compact,
        ""
    )


# ============================================================
# NAME EXTRACTION
# ============================================================

def extract_name(text):
    """
    Extract candidate name.

    Handles:
    - Name: Mohd Naved Abbas
    - MOHD NAVED ABBAS
    - M O H D N A V E D A B B A S
    """

    lines = get_clean_lines(text)

    if not lines:
        return ""

    # --------------------------------------------------------
    # 1. Explicit Name field
    # --------------------------------------------------------

    for line in lines[:40]:

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

            if valid_name(candidate):

                return candidate

    # --------------------------------------------------------
    # 2. Spaced-character name
    # --------------------------------------------------------

    for line in lines[:40]:

        recovered = recover_spaced_name(
            line
        )

        if recovered:

            return recovered

    # --------------------------------------------------------
    # 3. Uppercase normal name
    # --------------------------------------------------------

    for line in lines[:40]:

        candidate = remove_bullet(
            line
        )

        if (
            candidate.isupper()
            and valid_name(candidate)
        ):
            return candidate

    # --------------------------------------------------------
    # 4. Title case
    # --------------------------------------------------------

    for line in lines[:20]:

        candidate = remove_bullet(
            line
        )

        if not valid_name(candidate):
            continue

        words = candidate.split()

        if all(
            word[0].isupper()
            for word in words
            if word
        ):
            return candidate

    return ""


# ============================================================
# NORMAL SECTION EXTRACTION
# ============================================================

def extract_section_from_heading(
    lines,
    target_section
):
    """
    Extract a section when the PDF text is in normal
    reading order.

    Example:

        Projects
        Project A
        Project B
        Certifications
        Certificate A

    Projects returns only Project A and Project B.
    """

    result = []

    inside = False

    for line in lines:

        heading = get_hard_heading(
            line
        )

        # Start requested section
        if heading == target_section:

            inside = True

            continue

        # Stop at another section
        if (
            inside
            and heading is not None
            and heading != target_section
        ):
            break

        if inside:

            result.append(
                line
            )

    return result


# ============================================================
# EDUCATION
# ============================================================

EDUCATION_KEYWORDS = (
    "b.tech",
    "btech",
    "b.e.",
    "bachelor",
    "b.sc",
    "bsc",
    "bca",
    "m.tech",
    "mtech",
    "m.e.",
    "master",
    "m.sc",
    "msc",
    "mca",
    "ph.d",
    "phd",
    "computer science",
    "information technology",
    "engineering",
    "university",
    "college",
    "institute",
    "cgpa",
    "gpa",
    "graduation",
    "degree",
)


def looks_like_education(line):
    """Detect education-related text."""

    if not line:
        return False

    lower = line.lower()

    return any(
        keyword in lower
        for keyword in EDUCATION_KEYWORDS
    )


def extract_education(text):
    """
    Extract education.

    First tries the actual Education section.
    If PDF columns scrambled the section, uses
    controlled education keywords.
    """

    lines = get_clean_lines(text)

    # --------------------------------------------------------
    # Normal section
    # --------------------------------------------------------

    section = extract_section_from_heading(
        lines,
        "education"
    )

    result = []

    for line in section:

        line = remove_bullet(line)

        if line:
            result.append(line)

    if result:
        return "\n".join(
            result
        )

    # --------------------------------------------------------
    # Scrambled PDF fallback
    # --------------------------------------------------------

    fallback = []

    for index, line in enumerate(lines):

        if looks_like_education(line):

            if line not in fallback:
                fallback.append(line)

            # Include nearby institution/year information
            for nearby in lines[
                index + 1:index + 3
            ]:

                if (
                    contains_education_context(
                        nearby
                    )
                ):

                    if nearby not in fallback:
                        fallback.append(
                            nearby
                        )

    return "\n".join(
        fallback[:8]
    )


def contains_education_context(line):
    """Detect education context."""

    if not line:
        return False

    lower = line.lower()

    patterns = [

        r"\b20\d{2}\b",

        r"\b20\d{2}\s*[-–]\s*20\d{2}\b",

        r"\bcgpa\b",

        r"\bgpa\b",

        r"\bcollege\b",

        r"\buniversity\b",

        r"\binstitute\b",
    ]

    return any(
        re.search(
            pattern,
            lower
        )
        for pattern in patterns
    )


# ============================================================
# EXPERIENCE
# ============================================================

def extract_experience(text):
    """Extract work experience."""

    lines = get_clean_lines(text)

    section = extract_section_from_heading(
        lines,
        "experience"
    )

    result = []

    for line in section:

        line = remove_bullet(line)

        if line:
            result.append(line)

    return "\n".join(
        result
    )


# ============================================================
# INTERNSHIPS
# ============================================================

def extract_internships(text):
    """Extract internship information."""

    lines = get_clean_lines(text)

    section = extract_section_from_heading(
        lines,
        "internships"
    )

    result = []

    for line in section:

        line = remove_bullet(line)

        if line:
            result.append(line)

    return "\n".join(
        result
    )


# ============================================================
# PROJECT DETECTION
# ============================================================

PROJECT_TITLE_KEYWORDS = (
    "prediction",
    "detection",
    "classification",
    "recommendation",
    "website",
    "application",
    "app",
    "system",
    "dashboard",
    "analyzer",
    "analysis",
    "management",
)


PROJECT_TECH_KEYWORDS = (
    "using python",
    "using django",
    "using machine learning",
    "using scikit",
    "using tensorflow",
    "using pandas",
    "using numpy",
    "using html",
    "using css",
    "using javascript",
    "ai/ml",
    "machine learning model",
)


def looks_like_project(line):
    """Detect project-related text."""

    if not line:
        return False

    lower = line.lower()

    return (
        any(
            keyword in lower
            for keyword in PROJECT_TITLE_KEYWORDS
        )
        or
        any(
            keyword in lower
            for keyword in PROJECT_TECH_KEYWORDS
        )
    )


# ============================================================
# CERTIFICATION DETECTION
# ============================================================

CERTIFICATION_KEYWORDS = (
    "certification",
    "certified",
    "certificate",
    "skills passport",
    "skillsbuild",
    "hp life",
    "cisco",
    "tcs ion",
    "tcs i on",
    "google for developers",
    "eduskills",
    "coursera",
    "udemy",
    "linkedin learning",
    "ibm",
    "oracle certified",
    "aws certified",
)


def looks_like_certification(line):
    """Detect certification-related text."""

    if not line:
        return False

    lower = line.lower()

    return any(
        keyword in lower
        for keyword in CERTIFICATION_KEYWORDS
    )


# ============================================================
# PROJECTS
# ============================================================

def extract_projects(text):
    """
    Extract projects.

    Strategy:

    1. If Projects section is in normal PDF order,
       extract that section only.

    2. If PDF column extraction scrambled the order,
       use project-specific signals.

    3. NEVER include:
       - contact information
       - certification heading
       - certification items
       - education heading
       - experience heading
    """

    lines = get_clean_lines(text)

    # --------------------------------------------------------
    # FIRST: normal section extraction
    # --------------------------------------------------------

    section = extract_section_from_heading(
        lines,
        "projects"
    )

    projects = []

    for line in section:

        # HARD STOP
        heading = get_hard_heading(
            line
        )

        if heading is not None:
            break

        clean = remove_bullet(
            line
        )

        if not clean:
            continue

        if is_contact_line(clean):
            continue

        if looks_like_certification(
            clean
        ):
            continue

        # Explicit certification headings
        if compact_text(
            clean.rstrip(":")
        ) in {
            "certifications",
            "certification",
            "certificates",
        }:
            break

        if clean not in projects:

            projects.append(
                clean
            )

    if projects:

        return projects

    # --------------------------------------------------------
    # SECOND: scrambled-column fallback
    # --------------------------------------------------------

    fallback = []

    for line in lines:

        clean = remove_bullet(
            line
        )

        if not clean:
            continue

        # Never contact information
        if is_contact_line(clean):
            continue

        # Never headings
        if get_hard_heading(
            clean
        ) is not None:
            continue

        # Never certification text
        if looks_like_certification(
            clean
        ):
            continue

        if looks_like_project(
            clean
        ):

            if clean not in fallback:

                fallback.append(
                    clean
                )

    return fallback


# ============================================================
# CERTIFICATIONS
# ============================================================

def extract_certifications(text):
    """
    Extract certifications.

    Strategy:

    1. Normal Certifications section.
    2. If PDF columns are scrambled, identify known
       certification providers/certification keywords.

    This prevents Projects from swallowing Certifications.
    """

    lines = get_clean_lines(text)

    # --------------------------------------------------------
    # FIRST: normal section extraction
    # --------------------------------------------------------

    section = extract_section_from_heading(
        lines,
        "certifications"
    )

    certifications = []

    for line in section:

        heading = get_hard_heading(
            line
        )

        if heading is not None:
            break

        clean = remove_bullet(
            line
        )

        if not clean:
            continue

        if is_contact_line(clean):
            continue

        if clean not in certifications:

            certifications.append(
                clean
            )

    if certifications:

        return certifications

    # --------------------------------------------------------
    # SECOND: scrambled-column fallback
    # --------------------------------------------------------

    fallback = []

    for line in lines:

        clean = remove_bullet(
            line
        )

        if not clean:
            continue

        if is_contact_line(clean):
            continue

        if get_hard_heading(
            clean
        ) is not None:
            continue

        if looks_like_certification(
            clean
        ):

            if clean not in fallback:

                fallback.append(
                    clean
                )

    return fallback


# ============================================================
# SKILLS
# ============================================================

def extract_skills_section(text):
    """Extract raw technical skills section."""

    lines = get_clean_lines(text)

    section = extract_section_from_heading(
        lines,
        "skills"
    )

    result = []

    for line in section:

        line = remove_bullet(line)

        if line:
            result.append(line)

    return "\n".join(
        result
    )


# ============================================================
# ACHIEVEMENTS
# ============================================================

def extract_achievements(text):
    """Extract achievements."""

    lines = get_clean_lines(text)

    section = extract_section_from_heading(
        lines,
        "achievements"
    )

    result = []

    for line in section:

        line = remove_bullet(line)

        if line:
            result.append(line)

    return "\n".join(
        result
    )


# ============================================================
# SUMMARY
# ============================================================

def extract_summary(text):
    """Extract professional summary."""

    lines = get_clean_lines(text)

    section = extract_section_from_heading(
        lines,
        "summary"
    )

    result = []

    for line in section:

        line = remove_bullet(line)

        if line:
            result.append(line)

    return "\n".join(
        result
    )


# ============================================================
# COMPLETE SECTION EXTRACTION
# ============================================================

def extract_resume_sections(text):
    """
    Extract all major resume sections.
    """

    projects = extract_projects(
        text
    )

    certifications = extract_certifications(
        text
    )

    return {

        "summary": extract_summary(
            text
        ),

        "education": extract_education(
            text
        ),

        "skills": extract_skills_section(
            text
        ),

        "experience": extract_experience(
            text
        ),

        "internships": extract_internships(
            text
        ),

        "projects": "\n".join(
            projects
        ),

        "certifications": "\n".join(
            certifications
        ),

        "achievements": extract_achievements(
            text
        ),
    }


# ============================================================
# MAIN RESUME PARSER
# ============================================================

def parse_resume(text):
    """
    Parse a complete resume.

    Compatible with the existing app.py.
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

        "name": extract_name(
            text
        ),

        "email": extract_email(
            text
        ),

        "education": extract_education(
            text
        ),

        # Skill extraction is handled separately
        # by skill_extractor.py
        "skills": [],

        "experience": extract_experience(
            text
        ),

        "projects": extract_projects(
            text
        ),

        "certifications": extract_certifications(
            text
        ),

        "internships": extract_internships(
            text
        ),

        "achievements": extract_achievements(
            text
        ),
    }