"""Command-line entry point.

Run from the project folder:
    python -m src.main --resume data/samples/sample_resume.txt --job data/samples/sample_job_description.txt
"""
import argparse
import sys

from src.job_analyzer import analyze_job_description
from src.recommendation_engine import generate_recommendations, identify_strengths, has_measurable_results
from src.resume_parser import ResumeParseError, detect_sections, extract_text
from src.similarity_engine import compute_similarity, match_skills, to_percentage
from src.skill_extractor import extract_skills

DISCLAIMER = (
    "The score measures textual alignment between the resume and the job description. "
    "It is NOT a prediction of whether you will be hired."
)


def analyze(resume_path: str, job_text: str) -> dict:
    """Run the full pipeline and return all report fields as a dictionary."""
    resume_text = extract_text(resume_path)
    job = analyze_job_description(job_text)

    resume_skills = extract_skills(resume_text)
    sections = detect_sections(resume_text)
    similarity = compute_similarity(resume_text, job_text)
    matched, missing, coverage = match_skills(resume_skills, job["skills"])

    return {
        "filename": resume_path,
        "sections": sections,
        "resume_skills": resume_skills,
        "job_skills": job["skills"],
        "job_keywords": job["keywords"],
        "job_warnings": job["warnings"],
        "matched_skills": matched,
        "missing_skills": missing,
        "skill_coverage": coverage,
        "score": to_percentage(similarity),
        "strengths": identify_strengths(sections, matched, resume_text),
        "recommendations": generate_recommendations(
            resume_text, sections, matched, missing, to_percentage(similarity)
        ),
        "has_measurable_results": has_measurable_results(resume_text),
    }


def _bullets(items: list[str]) -> str:
    return "\n".join(f"  - {item}" for item in items) if items else "  None"


def format_report(report: dict) -> str:
    """Build the structured text report (the 10 items from the project brief)."""
    lines = [
        "=" * 60,
        "SMART AI RESUME ANALYZER - REPORT",
        "=" * 60,
        f"1. Resume filename: {report['filename']}",
        f"2. Detected sections: {', '.join(report['sections']) or 'None found'}",
        f"3. Extracted skills: {', '.join(report['resume_skills']) or 'None found'}",
        f"4. Job description skills: {', '.join(report['job_skills']) or 'None found'}",
        f"   Other frequent terms: {', '.join(report['job_keywords'])}",
        f"5. Matching skills: {', '.join(report['matched_skills']) or 'None'}",
        f"6. Missing skills: {', '.join(report['missing_skills']) or 'None'}",
        f"7. Compatibility score: {report['score']} / 100  (skill coverage: {report['skill_coverage']}%)",
        "8. Resume strengths:",
        _bullets(report["strengths"]),
        "9. Improvement recommendations:",
        _bullets(report["recommendations"]),
        "10. Final summary:",
        f"  {len(report['matched_skills'])} of {len(report['job_skills'])} job skills found in the resume. "
        f"Score {report['score']}/100.",
        f"  {DISCLAIMER}",
    ]
    for warning in report["job_warnings"]:
        lines.append(f"  WARNING: {warning}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare a resume with a job description.")
    parser.add_argument("--resume", required=True, help="Path to a .pdf, .docx or .txt resume")
    parser.add_argument("--job", required=True, help="Path to a .txt file containing the job description")
    args = parser.parse_args(argv)

    try:
        with open(args.job, encoding="utf-8", errors="replace") as handle:
            job_text = handle.read()
    except OSError as exc:
        print(f"Error: could not read job description: {exc}")
        return 1

    try:
        report = analyze(args.resume, job_text)
    except (ResumeParseError, FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}")
        return 1

    print(format_report(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
