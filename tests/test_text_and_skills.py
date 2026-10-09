"""Tests for text preprocessing and rule-based skill extraction."""
from src.skill_extractor import extract_skills
from src.text_preprocessing import clean_text, preprocess, tokenize


def test_tokenize_keeps_technical_terms_whole():
    tokens = tokenize("Experienced in C++, C#, Node.js and .NET.")
    assert "c++" in tokens
    assert "c#" in tokens
    assert "node.js" in tokens
    assert "dotnet" in tokens


def test_clean_text_lowercases_and_removes_bullets():
    assert clean_text("• Python   and\nSQL") == "python and sql"


def test_preprocess_removes_stopwords():
    assert "the" not in preprocess("The model is trained on the data").split()


def test_special_terms_are_detected():
    skills = extract_skills("Experienced in C++, C#, .NET, Node.js and JavaScript.")
    assert {"c++", "c#", "dotnet", "node.js", "javascript"} <= set(skills)


def test_java_not_detected_inside_javascript():
    assert "java" not in extract_skills("I write JavaScript daily.")


def test_react_not_detected_inside_reactive():
    assert "react" not in extract_skills("Built reactive pipelines for streaming data.")


def test_aliases_are_mapped_to_canonical_names():
    skills = extract_skills("Deployed on Amazon Web Services and managed k8s clusters.")
    assert "aws" in skills
    assert "kubernetes" in skills


def test_unknown_text_returns_no_skills():
    assert extract_skills("Enjoys hiking and cooking on weekends.") == []
