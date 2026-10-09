"""Streamlit web interface for Smart AI Resume Analyzer.

Run from the project folder:
    streamlit run app.py
"""
import os
import tempfile
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from src.main import DISCLAIMER, analyze, format_report
from src.pdf_generator import generate_pdf_report
from src.resume_parser import ResumeParseError

# Sample files paths for instant demo
SAMPLES_DIR = Path(__file__).parent / "data" / "samples"
SAMPLE_RESUME_PATH = SAMPLES_DIR / "sample_resume.txt"
SAMPLE_JOB_PATH = SAMPLES_DIR / "sample_job_description.txt"

# Page configuration
st.set_page_config(
    page_title="Smart AI Resume Analyzer | Pro Report",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Initialize Session State Keys for reliable resets
if "reset_count" not in st.session_state:
    st.session_state["reset_count"] = 0

if "job_input" not in st.session_state:
    st.session_state["job_input"] = ""

if "use_demo" not in st.session_state:
    st.session_state["use_demo"] = False

# Dark Theme CSS
DARK_THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background-color: #090d16 !important;
    color: #f8fafc !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

[data-testid="stSidebar"] {
    background-color: #0f172a !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
}

.main .block-container {
    max-width: 1140px;
    padding-top: 1.5rem;
    padding-bottom: 3.5rem;
    padding-left: 1.5rem;
    padding-right: 1.5rem;
}

/* Header Bar */
.report-header {
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding-bottom: 1.25rem;
    margin-bottom: 1.5rem;
}

.report-title {
    font-size: 1.8rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 0.35rem 0;
}

.report-subtitle {
    font-size: 0.95rem;
    color: #94a3b8;
    margin: 0;
}

/* Metric Card Grid */
.metric-card {
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 1.1rem 1.25rem;
    text-align: left;
    backdrop-filter: blur(10px);
}

.metric-card-label {
    font-size: 0.78rem;
    font-weight: 700;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.35rem;
}

.metric-card-value {
    font-size: 1.6rem;
    font-weight: 800;
    color: #818cf8;
    margin: 0;
}

.metric-card-value-green {
    color: #34d399;
}

/* Report Section Containers */
.report-section {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(12px);
}

.section-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #f8fafc;
    margin-bottom: 1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding-bottom: 0.5rem;
}

.explanation-box {
    background: rgba(30, 41, 59, 0.5);
    border-left: 4px solid #6366f1;
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.25rem;
    font-size: 0.92rem;
    color: #cbd5e1;
    line-height: 1.6;
}

/* Skill Badges */
.skills-group {
    margin-bottom: 1.25rem;
}

.skills-group-title {
    font-size: 0.9rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.badge-wrapper {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.badge-matched {
    background: rgba(16, 185, 129, 0.15);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.3);
    padding: 0.35rem 0.75rem;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 500;
}

.badge-additional {
    background: rgba(59, 130, 246, 0.15);
    color: #60a5fa;
    border: 1px solid rgba(59, 130, 246, 0.3);
    padding: 0.35rem 0.75rem;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 500;
}

.badge-missing {
    background: rgba(245, 158, 11, 0.15);
    color: #fbbf24;
    border: 1px solid rgba(245, 158, 11, 0.3);
    padding: 0.35rem 0.75rem;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 500;
}

.badge-none {
    color: #34d399;
    font-size: 0.9rem;
    font-weight: 500;
}

/* Strength Cards */
.strength-card {
    background: rgba(30, 41, 59, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-left: 4px solid #10b981;
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
}

.strength-heading {
    font-size: 0.95rem;
    font-weight: 700;
    color: #34d399;
    margin-bottom: 0.25rem;
}

.strength-body {
    font-size: 0.88rem;
    color: #cbd5e1;
    line-height: 1.5;
}

.strength-evidence {
    font-size: 0.82rem;
    color: #94a3b8;
    margin-top: 0.35rem;
    font-style: italic;
}

/* Recommendation Steps */
.recommendation-step {
    background: rgba(30, 41, 59, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.85rem;
}

.step-number {
    display: inline-block;
    background: #4f46e5;
    color: #ffffff;
    font-size: 0.75rem;
    font-weight: 700;
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    margin-bottom: 0.5rem;
}

.step-what {
    font-size: 0.95rem;
    font-weight: 700;
    color: #f8fafc;
    margin-bottom: 0.35rem;
}

.step-detail {
    font-size: 0.88rem;
    color: #cbd5e1;
    line-height: 1.5;
    margin-bottom: 0.25rem;
}

/* Summary Callout */
.summary-box {
    background: rgba(30, 27, 75, 0.5);
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 10px;
    padding: 1.25rem;
    margin-bottom: 1.5rem;
}

.summary-title {
    font-size: 1rem;
    font-weight: 700;
    color: #a5b4fc;
    margin-bottom: 0.5rem;
}

.summary-text {
    font-size: 0.92rem;
    color: #f1f5f9;
    line-height: 1.6;
    margin-bottom: 0.75rem;
}

.disclaimer-text {
    font-size: 0.82rem;
    color: #94a3b8;
    margin: 0;
}

/* Inputs & Widgets Overrides */
[data-testid="stTextArea"] textarea {
    background: rgba(15, 23, 42, 0.75) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 10px !important;
    color: #f8fafc !important;
}

[data-testid="stFileUploader"] {
    background: rgba(15, 23, 42, 0.6) !important;
    border: 2px dashed rgba(99, 102, 241, 0.35) !important;
    border-radius: 12px !important;
}

button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
    border: none !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    font-weight: 700 !important;
}

@media (max-width: 768px) {
    .metric-card-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
"""

st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)

# Main Application Header
st.markdown(
    """
    <div class="report-header">
        <h1 class="report-title">⚡ Smart AI Resume Analyzer</h1>
        <p class="report-subtitle">Objective ATS compatibility analysis, skill extraction, and document evaluation</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar Controls
with st.sidebar:
    st.markdown("### Controls & Testing")

    if st.button("✨ Load Demo Data", use_container_width=True):
        st.session_state["use_demo"] = True
        if SAMPLE_JOB_PATH.exists():
            st.session_state["job_input"] = SAMPLE_JOB_PATH.read_text(encoding="utf-8")
        st.rerun()

    if st.button("🗑️ Reset All Inputs", use_container_width=True):
        st.session_state["use_demo"] = False
        st.session_state["job_input"] = ""
        st.session_state["reset_count"] += 1
        st.rerun()

    st.markdown("---")
    st.markdown("**Supported Formats**")
    st.markdown("• PDF (`.pdf`)\n• Word (`.docx`)\n• Text (`.txt`)")

# Input Controls
use_demo = st.session_state.get("use_demo", False)

col1, col2 = st.columns(2, gap="medium")

with col1:
    st.subheader("1. Resume Document")
    if use_demo:
        st.info("Demo mode active (`sample_resume.txt`). Upload a file to override.")
        resume_file = None
    else:
        resume_file = st.file_uploader(
            "Upload Resume",
            type=["pdf", "docx", "txt"],
            label_visibility="collapsed",
            key=f"uploader_{st.session_state['reset_count']}",
        )
    if resume_file:
        st.caption(f"File loaded: `{resume_file.name}`")

with col2:
    st.subheader("2. Target Job Description")
    default_job_text = st.session_state.get("job_input", "")
    job_text = st.text_area(
        "Job Description Text",
        value=default_job_text,
        height=180,
        placeholder="Paste target job description text here...",
        label_visibility="collapsed",
        key=f"text_area_{st.session_state['reset_count']}",
    )
    if job_text.strip():
        st.caption(f"Job description word count: {len(job_text.split())} words")

st.markdown("<br>", unsafe_allow_html=True)
analyze_clicked = st.button("Analyze Resume Alignment", type="primary", use_container_width=True)

# Process Analysis
if analyze_clicked or (use_demo and job_text.strip()):
    tmp_path = None
    try:
        if not use_demo and resume_file is None:
            st.error("Please upload a resume document or click 'Load Demo Data'.")
        elif not job_text.strip():
            st.error("Please paste a target job description.")
        else:
            with st.spinner("Analyzing document structure and skill alignment..."):
                if use_demo and resume_file is None:
                    tmp_path = str(SAMPLE_RESUME_PATH)
                else:
                    suffix = os.path.splitext(resume_file.name)[1].lower()
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        tmp.write(resume_file.getbuffer())
                        tmp_path = tmp.name

                report = analyze(tmp_path, job_text)

            # Determine Target Job Title from first line
            job_lines = [l.strip() for l in job_text.strip().splitlines() if l.strip()]
            job_title = job_lines[0] if job_lines else "Target Position"
            if len(job_title) > 60:
                job_title = job_title[:57] + "..."

            # Top Navigation Tabs
            tab_main, tab_details, tab_export = st.tabs([
                "📊 Analysis Report",
                "🔑 Detailed Keywords & Skills",
                "📄 Actions & Plain Text",
            ])

            with tab_main:
                # 1. Top Dashboard Header & Metric Cards
                st.markdown(
                    f"""
                    <div style="margin-bottom: 1rem;">
                        <h2 style="font-size: 1.4rem; font-weight: 700; color: #ffffff; margin: 0;">Resume Analysis Report</h2>
                        <p style="font-size: 0.9rem; color: #94a3b8; margin: 0.2rem 0 0 0;">Target Position: <strong style="color: #818cf8;">{job_title}</strong></p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                m_col1, m_col2, m_col3, m_col4 = st.columns(4)
                with m_col1:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-card-label">Compatibility Score</div>
                            <div class="metric-card-value">{report['score']}/100</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with m_col2:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-card-label">Skill Coverage</div>
                            <div class="metric-card-value">{report['skill_coverage']}%</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with m_col3:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-card-label">Matched Skills</div>
                            <div class="metric-card-value metric-card-value-green">{len(report['matched_skills'])} / {len(report['job_skills'])}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with m_col4:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-card-label">Recognized Sections</div>
                            <div class="metric-card-value">{len(report['sections'])}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                st.markdown("<br>", unsafe_allow_html=True)

                # 2. What Does Your Score Mean?
                st.markdown(
                    f"""
                    <div class="report-section">
                        <div class="section-title">What Does Your Score Mean?</div>
                        <div class="explanation-box">
                            <strong>Understanding the distinction between metrics:</strong><br>
                            • <strong>Compatibility Score ({report['score']}/100):</strong> Evaluates total textual alignment between the entire preprocessed resume and the job posting using TF-IDF vector cosine similarity. It measures vocabulary overlap, contextual phrasing, and duty descriptions across the entire document.<br>
                            • <strong>Skill Coverage ({report['skill_coverage']}%):</strong> Measures the percentage of required skills from the job description detected in your resume ({len(report['matched_skills'])} of {len(report['job_skills'])} skills matched).<br><br>
                            <strong>Why metrics may differ:</strong> In this evaluation, you matched <strong>{report['skill_coverage']}%</strong> of explicit required skills. However, the overall compatibility score is <strong>{report['score']}/100</strong> because the job description contains broader context, qualification phrasing, and domain terminology that extend beyond the skill list alone.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # 3. Skills Match Analysis
                additional_skills = [s for s in report.get("resume_skills", []) if s not in report.get("job_skills", [])]

                matched_badges = "".join(f'<span class="badge-matched">✓ {s}</span>' for s in report["matched_skills"]) or '<span class="badge-none">None detected</span>'
                additional_badges = "".join(f'<span class="badge-additional">{s}</span>' for s in additional_skills) or '<span class="badge-none">None</span>'
                if report["missing_skills"]:
                    missing_badges = "".join(f'<span class="badge-missing">+ {s}</span>' for s in report["missing_skills"])
                else:
                    missing_badges = '<span class="badge-none">No missing required skills.</span>'

                st.markdown(
                    f"""
                    <div class="report-section">
                        <div class="section-title">Skills Match Analysis</div>
                        <div class="skills-group">
                            <div class="skills-group-title" style="color: #34d399;">Matched Skills ({len(report['matched_skills'])})</div>
                            <div class="badge-wrapper">{matched_badges}</div>
                        </div>
                        <div class="skills-group">
                            <div class="skills-group-title" style="color: #60a5fa;">Additional Skills Found ({len(additional_skills)})</div>
                            <div class="badge-wrapper">{additional_badges}</div>
                        </div>
                        <div class="skills-group" style="margin-bottom: 0;">
                            <div class="skills-group-title" style="color: #fbbf24;">Missing Required Skills ({len(report['missing_skills'])})</div>
                            <div class="badge-wrapper">{missing_badges}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # 4. What Your Resume Does Well
                st.markdown('<div class="report-section"><div class="section-title">What Your Resume Does Well</div>', unsafe_allow_html=True)

                # Card 1: Skill Coverage
                matched_count = len(report["matched_skills"])
                total_job_skills = len(report["job_skills"])
                if total_job_skills > 0 and matched_count == total_job_skills:
                    st.markdown(
                        f"""
                        <div class="strength-card">
                            <div class="strength-heading">Strong Keyword Alignment</div>
                            <div class="strength-body">All {total_job_skills} required skills identified in the job posting were detected in your resume text.</div>
                            <div class="strength-evidence">Supporting evidence: Detected skills include {', '.join(report['matched_skills'])}.</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                elif matched_count > 0:
                    st.markdown(
                        f"""
                        <div class="strength-card">
                            <div class="strength-heading">Partial Skill Alignment</div>
                            <div class="strength-body">Detected {matched_count} out of {total_job_skills} required skills in your resume ({report['skill_coverage']}% coverage).</div>
                            <div class="strength-evidence">Supporting evidence: Matched skills: {', '.join(report['matched_skills'])}.</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # Card 2: Recognized Structure
                if len(report["sections"]) >= 4:
                    st.markdown(
                        f"""
                        <div class="strength-card">
                            <div class="strength-heading">Recognized Resume Structure</div>
                            <div class="strength-body">{len(report['sections'])} standard section headings were identified, helping ATS parsers index your background.</div>
                            <div class="strength-evidence">Supporting evidence: Detected headings: {', '.join(report['sections'])}.</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # Card 3: Measurable Achievements
                if report.get("has_measurable_results"):
                    st.markdown(
                        """
                        <div class="strength-card">
                            <div class="strength-heading">Measurable Achievements</div>
                            <div class="strength-body">Quantifiable metrics (numbers tied to units, percentages, or scale indicators) were detected in your resume statements.</div>
                            <div class="strength-evidence">Supporting evidence: Statement patterns containing numerical units (e.g. %, counts, project scale).</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                st.markdown('</div>', unsafe_allow_html=True)

                # 5. Recommended Improvements
                st.markdown('<div class="report-section"><div class="section-title">Recommended Improvements</div>', unsafe_allow_html=True)

                step_idx = 1
                # Rule A: Textual alignment if score is below 70
                if report["score"] < 70:
                    kw_sample = ", ".join(report.get("job_keywords", [])[:5]) or "target job terms"
                    st.markdown(
                        f"""
                        <div class="recommendation-step">
                            <span class="step-number">STEP {step_idx}</span>
                            <div class="step-what">Enhance Job Description Textual Alignment</div>
                            <div class="step-detail"><strong>Why it matters:</strong> While required skill keywords were detected, your overall compatibility score ({report['score']}/100) indicates low textual overlap with the job posting's terminology and responsibility descriptions.</div>
                            <div class="step-detail"><strong>Practical action:</strong> Incorporate contextual keywords and phrases from the job description (e.g., {kw_sample}) into your experience bullet points where accurately applicable.</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    step_idx += 1

                # Rule B: Missing skills (ONLY if missing_skills exist)
                if report["missing_skills"]:
                    missing_str = ", ".join(report["missing_skills"])
                    st.markdown(
                        f"""
                        <div class="recommendation-step">
                            <span class="step-number">STEP {step_idx}</span>
                            <div class="step-what">Address Missing Required Skills</div>
                            <div class="step-detail"><strong>Why it matters:</strong> The job description lists core requirements ({missing_str}) that were not detected in your resume.</div>
                            <div class="step-detail"><strong>Practical action:</strong> If you have experience with these tools, add them explicitly. If not, consider gaining familiarity before applying.</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    step_idx += 1

                # Rule C: Missing standard sections
                missing_sections = [s for s in ["Summary", "Education", "Experience", "Projects", "Skills"] if s not in report["sections"]]
                if missing_sections:
                    st.markdown(
                        f"""
                        <div class="recommendation-step">
                            <span class="step-number">STEP {step_idx}</span>
                            <div class="step-what">Add Missing Standard Headings ({', '.join(missing_sections)})</div>
                            <div class="step-detail"><strong>Why it matters:</strong> Automated applicant tracking systems expect standardized headings to categorize your qualifications accurately.</div>
                            <div class="step-detail"><strong>Practical action:</strong> Create clearly labeled section headers for {', '.join(missing_sections)}.</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    step_idx += 1

                # Rule D: Measurable results
                if not report.get("has_measurable_results"):
                    st.markdown(
                        f"""
                        <div class="recommendation-step">
                            <span class="step-number">STEP {step_idx}</span>
                            <div class="step-what">Quantify Project & Experience Achievements</div>
                            <div class="step-detail"><strong>Why it matters:</strong> Bullet points featuring numerical metrics demonstrate verifiable impact to hiring managers.</div>
                            <div class="step-detail"><strong>Practical action:</strong> Include specific numbers, percentages, record counts, or time savings in your achievement bullets.</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                st.markdown('</div>', unsafe_allow_html=True)

                # 6. Your Resume Analysis Summary
                st.markdown(
                    f"""
                    <div class="summary-box">
                        <div class="summary-title">Your Resume Analysis Summary</div>
                        <div class="summary-text">
                            Your resume contains <strong>{len(report['matched_skills'])} of {len(report['job_skills'])} skills</strong> identified as required for this job description (<strong>{report['skill_coverage']}%</strong> skill coverage). However, the overall compatibility score is <strong>{report['score']}/100</strong>. Because skill coverage and compatibility measure different aspects of document alignment, review the recommended improvements above to optimize your experience descriptions prior to submission.
                        </div>
                        <div class="disclaimer-text">
                            <strong>Disclaimer:</strong> {DISCLAIMER}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # 7. Functional Action Buttons
                pdf_bytes = generate_pdf_report(report, job_title)

                act_col1, act_col2, act_col3 = st.columns(3)
                with act_col1:
                    st.download_button(
                        label="📄 Download PDF Report",
                        data=pdf_bytes,
                        file_name="resume_analysis_report.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )

                with act_col2:
                    if st.button("🖨️ Print Report", use_container_width=True):
                        components.html("<script>window.print();</script>", height=0)

                with act_col3:
                    if st.button("🔄 Analyze Another Resume", use_container_width=True):
                        st.session_state["use_demo"] = False
                        st.session_state["job_input"] = ""
                        st.session_state["reset_count"] += 1
                        st.rerun()

            with tab_details:
                st.subheader("Detailed Keyword & Skill Inventory")

                k_col1, k_col2 = st.columns(2)
                with k_col1:
                    st.markdown("#### All Resume Skills Detected")
                    st.write(", ".join(report.get("resume_skills", [])) or "None identified")

                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("#### All Job Description Skills")
                    st.write(", ".join(report.get("job_skills", [])) or "None identified")

                with k_col2:
                    st.markdown("#### Frequent Job Posting Terms")
                    st.write(", ".join(report.get("job_keywords", [])) or "None identified")

            with tab_export:
                st.subheader("Plain Text Summary & Downloads")
                rpt_text = format_report(report)
                st.code(rpt_text, language="text")

                st.download_button(
                    label="📥 Download Structured Report (.txt)",
                    data=rpt_text,
                    file_name="resume_analysis_report.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

    except (ResumeParseError, FileNotFoundError, ValueError) as exc:
        st.error(f"Analysis Error: {exc}")
    finally:
        if tmp_path and tmp_path != str(SAMPLE_RESUME_PATH) and os.path.exists(tmp_path):
            os.remove(tmp_path)