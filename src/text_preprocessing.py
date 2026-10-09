"""Step D of the pipeline: clean raw text and turn it into tokens.

Pipeline for one document:
    raw text -> clean_text -> tokenize -> remove_stopwords -> preprocess (joined string)
"""
import re

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

# A "token" is a run of letters/digits that may contain +, # or . inside it.
# This keeps technical terms whole: "c++", "c#", "node.js", "scikit-learn" is
# split at the hyphen (fine for matching), and "python." loses its final dot.
TOKEN_PATTERN = r"[a-z0-9]+(?:[+#.][a-z0-9]+)*[+#]*"
_TOKEN_RE = re.compile(TOKEN_PATTERN)

_BULLET_RE = re.compile(r"[•●▪◦►✓✔·|*•]+")
_WHITESPACE_RE = re.compile(r"\s+")
# ".NET" on its own becomes "dotnet" so it survives tokenization.
_DOTNET_RE = re.compile(r"(?<![a-z0-9])\.net\b")


def clean_text(text: str) -> str:
    """Lowercase the text, remove bullet symbols, and collapse whitespace."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    text = text.lower()
    text = _BULLET_RE.sub(" ", text)
    text = _DOTNET_RE.sub(" dotnet ", text)
    text = _WHITESPACE_RE.sub(" ", text)
    return text.strip()


def tokenize(text: str) -> list[str]:
    """Split cleaned text into tokens such as 'python', 'c++', 'node.js'."""
    return _TOKEN_RE.findall(clean_text(text))


def remove_stopwords(tokens: list[str]) -> list[str]:
    """Drop common English words ('the', 'and') and single characters."""
    return [t for t in tokens if t not in ENGLISH_STOP_WORDS and len(t) > 1]


def preprocess(text: str) -> str:
    """Full pipeline: returns a space-joined string ready for TF-IDF."""
    return " ".join(remove_stopwords(tokenize(text)))
