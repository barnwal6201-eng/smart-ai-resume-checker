"""Step C: analyze a job description into required skills and keywords."""
from collections import Counter

from src.skill_extractor import extract_skills
from src.text_preprocessing import remove_stopwords, tokenize

MIN_RECOGNISED_SKILLS = 3


def analyze_job_description(job_text: str, top_n: int = 10) -> dict:
    """Return the skills, frequent keywords and warnings for a job description.

    Raises:
        ValueError: the job description is empty or only whitespace.
    """
    if not isinstance(job_text, str) or not job_text.strip():
        raise ValueError("The job description is empty.")

    skills = extract_skills(job_text)

    # Frequent terms: a simple count of meaningful words. Useful for showing
    # what the posting emphasises, but not a substitute for the skill list.
    tokens = remove_stopwords(tokenize(job_text))
    counts = Counter(t for t in tokens if len(t) > 2 and not t.isdigit())
    keywords = [word for word, _ in counts.most_common(top_n)]

    warnings = []
    if len(skills) < MIN_RECOGNISED_SKILLS:
        warnings.append(
            f"Only {len(skills)} known skill(s) found in the job description. "
            "The analysis is less reliable; add a clear list of required skills."
        )

    return {"skills": skills, "keywords": keywords, "warnings": warnings}
