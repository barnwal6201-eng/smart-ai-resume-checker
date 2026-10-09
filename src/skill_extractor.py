"""Rule-based skill extraction (Step B and C).

Each canonical skill has a list of aliases (spellings people actually write).
A skill is detected when one of its aliases appears as a whole term. The
lookarounds stop partial matches: 'java' does not match inside 'javascript',
and 'react' does not match inside 'reactive'.
"""
import re

from src.text_preprocessing import clean_text

SKILL_ALIASES: dict[str, list[str]] = {
    # Programming languages
    "python": ["python"],
    "java": ["java"],
    "javascript": ["javascript"],
    "typescript": ["typescript"],
    "c++": ["c++", "cpp"],
    "c#": ["c#", "csharp"],
    "dotnet": ["dotnet", "asp.net"],
    "golang": ["golang"],
    "sql": ["sql"],
    "html": ["html", "html5"],
    "css": ["css", "css3"],
    # Frameworks and libraries
    "node.js": ["node.js", "nodejs"],
    "react": ["react", "react.js", "reactjs"],
    "numpy": ["numpy"],
    "pandas": ["pandas"],
    "matplotlib": ["matplotlib"],
    "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "tensorflow": ["tensorflow"],
    "pytorch": ["pytorch"],
    # Machine learning and data
    "machine learning": ["machine learning"],
    "deep learning": ["deep learning"],
    "nlp": ["nlp", "natural language processing"],
    "computer vision": ["computer vision"],
    "data analysis": ["data analysis", "data analytics"],
    "data visualization": ["data visualization", "data visualisation"],
    # Tools and platforms
    "git": ["git", "github"],
    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "aws": ["aws", "amazon web services"],
    "azure": ["azure", "microsoft azure"],
    "linux": ["linux"],
    "mysql": ["mysql"],
    "postgresql": ["postgresql", "postgres"],
    "mongodb": ["mongodb"],
    "excel": ["excel", "ms excel"],
    "tableau": ["tableau"],
    "power bi": ["power bi", "powerbi"],
    "hadoop": ["hadoop"],
    "spark": ["spark", "apache spark", "pyspark"],
    "rest api": ["rest api", "rest apis", "restful"],
    # Soft skills
    "communication": ["communication"],
    "teamwork": ["teamwork", "team player", "collaboration"],
    "leadership": ["leadership"],
    "problem solving": ["problem solving", "problem-solving"],
    "time management": ["time management"],
}


def _build_patterns() -> dict[str, re.Pattern]:
    """Compile one regex per skill. Longer aliases are tried first."""
    patterns = {}
    for skill, aliases in SKILL_ALIASES.items():
        alternatives = "|".join(re.escape(a) for a in sorted(aliases, key=len, reverse=True))
        # (?<!...) = not preceded by a term character; (?!...) = not followed by one.
        patterns[skill] = re.compile(rf"(?<![a-z0-9+#]) (?:{alternatives}) (?![a-z0-9+#])", re.VERBOSE)
    return patterns


_PATTERNS = _build_patterns()


def extract_skills(text: str) -> list[str]:
    """Return the sorted canonical skills found in the text."""
    cleaned = clean_text(text)
    return sorted(skill for skill, pattern in _PATTERNS.items() if pattern.search(cleaned))
