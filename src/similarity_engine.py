"""Step E: TF-IDF text matching, cosine similarity, and skill comparison.

How the score works:
1. Each document is preprocessed into a bag of meaningful words.
2. TF-IDF turns each document into a vector. Words that are common across
   documents get low weight; words that are distinctive get high weight.
3. Cosine similarity measures the angle between the two vectors:
   1.0 = same word profile, 0.0 = no shared weighted words.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.text_preprocessing import TOKEN_PATTERN, preprocess


def compute_similarity(resume_text: str, job_text: str) -> float:
    """Return the TF-IDF cosine similarity between resume and job text (0.0-1.0)."""
    documents = [preprocess(resume_text), preprocess(job_text)]
    if not documents[0] or not documents[1]:
        return 0.0  # nothing left to compare after cleaning

    # token_pattern keeps 'c++', 'c#' and 'node.js' as single features.
    vectorizer = TfidfVectorizer(token_pattern=TOKEN_PATTERN)
    matrix = vectorizer.fit_transform(documents)
    return float(cosine_similarity(matrix[0], matrix[1])[0][0])


def to_percentage(similarity: float) -> float:
    """Convert a 0-1 similarity into a 0-100 score with one decimal place."""
    return round(max(0.0, min(1.0, similarity)) * 100, 1)


def match_skills(resume_skills: list[str], job_skills: list[str]) -> tuple[list[str], list[str], float]:
    """Compare skill lists.

    Returns:
        matched: job skills the resume also lists.
        missing: job skills the resume does not list.
        coverage: percentage of job skills covered (0.0 if the job lists none).
    """
    resume_set = set(resume_skills)
    matched = [s for s in job_skills if s in resume_set]
    missing = [s for s in job_skills if s not in resume_set]
    coverage = round(len(matched) / len(job_skills) * 100, 1) if job_skills else 0.0
    return matched, missing, coverage
