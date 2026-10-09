"""Step F and G: strengths and improvement recommendations.

Every recommendation comes from a rule that checks the actual analysis.
Missing skills are never suggested as something to add to the resume unless
the candidate has used them; they are framed as things to learn.
"""
import re

REQUIRED_SECTIONS = ["Summary", "Education", "Experience", "Projects", "Skills"]

# Matches numbers attached to a unit, e.g. "40%", "12,000 records", "3x".
METRIC_RE = re.compile(
    r"\d+(?:[.,]\d+)?\s*%"
    r"|\d[\d,]*\+?\s*(?:users|customers|projects|students|records|rows|hours|days|"
    r"minutes|seconds|ms|times|x|employees|members|requests|tickets|reports|models)\b",
    re.IGNORECASE,
)


def has_measurable_results(text: str) -> bool:
    """True if the resume contains at least one number tied to a unit."""
    return bool(METRIC_RE.search(text))


def identify_strengths(sections: list[str], matched_skills: list[str], text: str) -> list[str]:
    strengths = []
    if matched_skills:
        strengths.append(f"Relevant skills that match the job: {', '.join(matched_skills)}.")
    if len(sections) >= 4:
        strengths.append(f"Well-structured resume with {len(sections)} recognised sections.")
    if has_measurable_results(text):
        strengths.append("Contains measurable results (numbers with units).")
    return strengths


def generate_recommendations(
    text: str,
    sections: list[str],
    matched_skills: list[str],
    missing_skills: list[str],
    similarity_score: float,
) -> list[str]:
    recommendations = []

    for section in REQUIRED_SECTIONS:
        if section not in sections:
            recommendations.append(f"Add a clearly labelled '{section}' section so recruiters' systems can find it.")

    if matched_skills:
        recommendations.append(
            "Move the matching skills into the top part of your resume: "
            + ", ".join(matched_skills) + "."
        )

    if missing_skills:
        recommendations.append(
            "The job lists these skills but your resume does not mention them: "
            + ", ".join(missing_skills)
            + ". Add one only if you have really used it. Otherwise, consider learning it."
        )

    if not has_measurable_results(text):
        recommendations.append(
            "Add measurable results to project and experience bullets, but only if they are true "
            "(for example: team size, records processed, time saved)."
        )

    if similarity_score < 30:
        recommendations.append(
            "The wording overlaps little with the job description. Where it truthfully describes "
            "your work, reuse the job's terminology."
        )

    return recommendations
