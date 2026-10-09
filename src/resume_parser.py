"""Step A and B: read resume files and detect their sections.

Supported formats: .pdf (pdfplumber), .docx (python-docx), and .txt (plain text,
included so the project can be tested without extra tools).
"""
import os
import re

import docx
import pdfplumber

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}

# Canonical section name -> heading variants that can appear in a resume.
SECTION_HEADINGS = {
    "Summary": {"summary", "profile", "objective", "career objective", "professional summary"},
    "Education": {"education", "academic background", "academics"},
    "Experience": {"experience", "work experience", "work history", "employment", "internships"},
    "Projects": {"projects", "academic projects", "personal projects"},
    "Skills": {"skills", "technical skills", "core competencies", "key skills"},
    "Certifications": {"certifications", "certificates", "licenses"},
    "Achievements": {"achievements", "awards", "accomplishments"},
}


class ResumeParseError(Exception):
    """Raised when a resume file cannot be read or contains no text."""


class UnsupportedFileError(ResumeParseError):
    """Raised when the file extension is not supported."""


def _read_pdf(path: str) -> str:
    with pdfplumber.open(path) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    return "\n".join(pages)


def _read_docx(path: str) -> str:
    document = docx.Document(path)
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


def _read_txt(path: str) -> str:
    with open(path, encoding="utf-8", errors="replace") as handle:
        return handle.read()


def extract_text(file_path: str) -> str:
    """Return the readable text of a resume file.

    Raises:
        FileNotFoundError: the path does not exist.
        UnsupportedFileError: the extension is not .pdf, .docx or .txt.
        ResumeParseError: the file is corrupted or contains no readable text.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Resume not found: {file_path}")

    extension = os.path.splitext(file_path)[1].lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFileError(
            f"Unsupported file type '{extension or 'none'}'. "
            f"Use one of: {', '.join(sorted(SUPPORTED_EXTENSIONS))}."
        )

    readers = {".pdf": _read_pdf, ".docx": _read_docx, ".txt": _read_txt}
    try:
        text = readers[extension](file_path)
    except Exception as exc:  # corrupted or password-protected files end up here
        raise ResumeParseError(f"Could not read '{os.path.basename(file_path)}': {exc}") from exc

    if not text.strip():
        raise ResumeParseError(
            f"'{os.path.basename(file_path)}' contains no readable text. "
            "If it is a scanned PDF, OCR is needed (not implemented)."
        )
    return text


def detect_sections(text: str) -> list[str]:
    """Return the canonical section names found, in the order they appear.

    A line counts as a heading only when, after removing punctuation and
    lowercasing, it exactly matches a known heading variant.
    """
    found: list[str] = []
    for line in text.splitlines():
        heading = re.sub(r"[^a-z ]", "", line.lower()).strip()
        for section_name, variants in SECTION_HEADINGS.items():
            if heading in variants and section_name not in found:
                found.append(section_name)
    return found
