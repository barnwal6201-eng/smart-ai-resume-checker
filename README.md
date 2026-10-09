# Smart AI Resume Analyzer

A Python project that compares a resume (PDF, DOCX, or TXT) with a job description. It extracts skills, computes a TF-IDF cosine-similarity score from 0 to 100, lists matching and missing skills, and gives improvement tips based on the analysis.

**What the score means:** it measures textual alignment between the two documents. It is **not** a prediction of whether you will be hired.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python -m src.main --resume data/samples/sample_resume.txt --job data/samples/sample_job_description.txt
python -m pytest -q
```

## Project structure

```
smart-ai-resume-analyzer/
├── data/samples/           sample resume and job description (fictional)
├── data/raw/               put downloaded datasets here (not used yet)
├── notebooks/              exploration notebooks (empty for now)
├── src/
│   ├── resume_parser.py    reads files, handles errors, detects sections
│   ├── text_preprocessing.py  cleaning, tokenizing, stop-word removal
│   ├── skill_extractor.py  rule-based skill detection with aliases
│   ├── job_analyzer.py     job description skills and frequent terms
│   ├── similarity_engine.py   TF-IDF, cosine similarity, skill matching
│   ├── recommendation_engine.py  strengths and recommendations
│   └── main.py             command-line entry point and report
├── tests/                  pytest tests
├── requirements.txt
└── README.md
```

## Techniques and why they were chosen

| Technique | Where | Why |
|---|---|---|
| Rule-based skill extraction | `skill_extractor.py` | Transparent and reliable for a known skill list. Easy to explain and debug. |
| Regex tokenization with special-character support | `text_preprocessing.py` | Keeps `c++`, `c#`, `node.js` intact, which generic tokenizers split. |
| TF-IDF | `similarity_engine.py` | Gives weight to distinctive words and reduces the effect of common ones. |
| Cosine similarity | `similarity_engine.py` | Compares document direction, so length differences matter less. |
| Set comparison | `similarity_engine.py` | Simple, exact way to find matched and missing skills. |

Not used yet: a supervised classifier, and semantic embeddings. See *Future work*.

## Deliberate choices

- **scikit-learn's English stop-word list** is used instead of NLTK. It avoids a data download and one fewer dependency. NLTK or spaCy can be added later for lemmatization.
- **TXT input** is supported in addition to PDF and DOCX so the project can be tested without extra files.
- **Recommendations never suggest adding a skill the candidate has not used.** Missing skills are presented as things to learn.

## Limitations

- The skill list is hand-written (about 50 skills). Skills not on the list are not detected.
- TF-IDF on only two documents gives a rough signal. Scores are usually low for good matches, so compare scores only across resumes against the same job.
- Scanned PDFs (images without text) are not supported. OCR is out of scope for now.
- Lemmatization is not implemented, so "analyzing" and "analysis" are treated as different words.

## Future work (not implemented)

- Lemmatization with NLTK or spaCy.
- Supervised classification on a labelled resume dataset, with accuracy, precision, recall, F1, and a confusion matrix.
- Semantic similarity with sentence embeddings.
- A larger, data-driven skill vocabulary.
