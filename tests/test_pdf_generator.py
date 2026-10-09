"""Tests for PDF report generator."""
from pathlib import Path
from src.main import analyze
from src.pdf_generator import generate_pdf_report

SAMPLES = Path(__file__).resolve().parent.parent / "data" / "samples"

def test_generate_pdf_report_returns_bytes():
    job_text = (SAMPLES / "sample_job_description.txt").read_text(encoding="utf-8")
    report = analyze(str(SAMPLES / "sample_resume.txt"), job_text)
    pdf_bytes = generate_pdf_report(report, "Junior Machine Learning Engineer")
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF-")
