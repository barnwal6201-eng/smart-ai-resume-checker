"""Tests for file handling, similarity, and the full pipeline."""
from pathlib import Path

import pytest

from src.main import analyze
from src.resume_parser import ResumeParseError, UnsupportedFileError, detect_sections, extract_text
from src.similarity_engine import compute_similarity, match_skills

SAMPLES = Path(__file__).resolve().parent.parent / "data" / "samples"


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        extract_text(str(tmp_path / "nope.txt"))


def test_unsupported_extension_raises(tmp_path):
    image = tmp_path / "resume.png"
    image.write_bytes(b"not really an image")
    with pytest.raises(UnsupportedFileError):
        extract_text(str(image))


def test_empty_file_raises(tmp_path):
    empty = tmp_path / "empty.txt"
    empty.write_text("   \n  ", encoding="utf-8")
    with pytest.raises(ResumeParseError):
        extract_text(str(empty))


def test_corrupted_pdf_raises(tmp_path):
    broken = tmp_path / "broken.pdf"
    broken.write_bytes(b"this is not a pdf")
    with pytest.raises(ResumeParseError):
        extract_text(str(broken))


def test_detect_sections_in_order():
    text = "Skills:\nPython\n\nEducation\nB.Tech\n\nProjects\nSpam classifier"
    assert detect_sections(text) == ["Skills", "Education", "Projects"]


def test_identical_texts_score_near_one():
    text = "Python machine learning with scikit-learn and pandas."
    assert compute_similarity(text, text) > 0.99


def test_unrelated_text_scores_lower_than_identical():
    resume = "Python machine learning with scikit-learn."
    unrelated = "Baking sourdough bread and growing tomatoes in the garden."
    assert compute_similarity(resume, unrelated) < compute_similarity(resume, resume)


def test_empty_resume_scores_zero():
    assert compute_similarity("", "Python developer needed") == 0.0


def test_match_skills_reports_missing_and_coverage():
    matched, missing, coverage = match_skills(["python", "sql"], ["python", "docker", "aws"])
    assert matched == ["python"]
    assert missing == ["docker", "aws"]
    assert coverage == pytest.approx(33.3, abs=0.1)


def test_full_pipeline_on_sample_files():
    job_text = (SAMPLES / "sample_job_description.txt").read_text(encoding="utf-8")
    report = analyze(str(SAMPLES / "sample_resume.txt"), job_text)

    assert 0 <= report["score"] <= 100
    assert "python" in report["matched_skills"]
    assert "docker" in report["missing_skills"]
    assert "aws" in report["missing_skills"]
    assert "Projects" in report["sections"]


def test_pipeline_rejects_empty_job_description():
    with pytest.raises(ValueError):
        analyze(str(SAMPLES / "sample_resume.txt"), "   ")
