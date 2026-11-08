import streamlit as st
import pandas as pd
import plotly.express as px

from analyzer import analyze_resume_job, extract_resume_text
from recommendations import get_recommendations
from report_generator import create_pdf_report

st.set_page_config(
    page_title="SkillLens | Resume Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: linear-gradient(135deg, rgba(37,99,235,.035), transparent 35%), var(--background-color); }
.hero { padding: 1.4rem 1.6rem; border: 1px solid rgba(100,116,139,.22); border-radius: 22px;
        background: linear-gradient(120deg, rgba(37,99,235,.12), rgba(14,165,233,.045)); margin-bottom: 1.2rem; }
.hero h1 { font-family: 'Manrope', sans-serif; font-weight: 800; letter-spacing: -.04em; margin: 0; }
.hero p { color: #64748b; margin: .45rem 0 0 0; font-size: 1.02rem; }
div[data-testid="stMetric"] { border: 1px solid rgba(100,116,139,.2); padding: 1rem; border-radius: 16px; background: rgba(127,127,127,.035); }
.section-label { font-size: .78rem; text-transform: uppercase; letter-spacing: .12em; color: #64748b; font-weight: 700; }
.skill-pill { display: inline-block; border-radius: 999px; padding: .3rem .65rem; margin: .15rem;
              background: rgba(34,197,94,.12); border: 1px solid rgba(34,197,94,.24); font-size: .88rem; }
.missing-pill { display: inline-block; border-radius: 999px; padding: .3rem .65rem; margin: .15rem;
                background: rgba(245,158,11,.12); border: 1px solid rgba(245,158,11,.25); font-size: .88rem; }
.small-muted { color: #64748b; font-size: .86rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="section-label">Career intelligence workspace</div>
  <h1>🎯 SkillLens</h1>
  <p>Understand your resume fit, discover skill gaps, and turn them into a focused learning plan.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## SkillLens")
    st.caption("Resume intelligence · NLP · Semantic matching")
    st.divider()
    st.markdown("### Analysis settings")
    use_semantic = st.toggle("Use semantic similarity", value=True,
        help="Uses a sentence-transformers model when installed and available. First use may download a model.")
    threshold = st.slider("Semantic match threshold", min_value=0.35, max_value=0.85, value=0.58, step=0.01,
        help="Higher values require stronger meaning similarity.")
    st.divider()
    st.markdown("### Privacy")
    st.write("Analysis runs in this app. With semantic matching enabled, the first model load may download a public model. Your resume text is not sent to a hosted AI API by this code.")
    st.caption("Use sample or redacted resumes for demos.")

upload_col, job_col = st.columns([0.85, 1.15], gap="large")
with upload_col:
    st.markdown("### 01 · Your resume")
    uploaded = st.file_uploader("Upload PDF or TXT", type=["pdf", "txt"])
    st.caption("Text-based PDFs work best. Scanned PDFs need OCR.")
with job_col:
    st.markdown("### 02 · Target role")
    role_title = st.text_input("Role title (optional)", placeholder="e.g. Python Developer Intern")
    job_text = st.text_area("Paste the job description", height=175,
        placeholder="Paste responsibilities, required skills, qualifications, and tools here…")

analyze = st.button("✨ Analyze resume fit", type="primary", use_container_width=True)

if analyze:
    if uploaded is None:
        st.error("Upload a PDF or TXT resume to continue.")
        st.stop()
    if not job_text.strip():
        st.error("Paste a job description to continue.")
        st.stop()
    try:
        resume_text = extract_resume_text(uploaded.getvalue(), uploaded.name)
        if len(resume_text.strip()) < 30:
            st.error("Not enough readable text was found. Try a text-based PDF or TXT file.")
            st.stop()
        with st.spinner("Comparing skills and meaning… the first semantic model load can take a little longer."):
            result = analyze_resume_job(resume_text, job_text, use_semantic=use_semantic, threshold=threshold)
    except Exception as exc:
        st.error(f"Analysis could not be completed: {exc}")
        st.stop()

    if not result["required_skills"]:
        st.warning("The job description did not contain skills from the supported skill library. Try adding specific skills such as Python, SQL, Git, Flask, React, or Machine Learning.")
        st.stop()

    st.session_state["result"] = result
    st.session_state["recommendations"] = get_recommendations(result["missing_skills"])
    st.session_state["resume_name"] = uploaded.name
    st.session_state["role_title"] = role_title.strip() or "Target role"

if "result" in st.session_state:
    result = st.session_state["result"]
    recommendations = st.session_state["recommendations"]
    st.divider()
    st.markdown("### 03 · Analysis overview")
    st.caption(f"Role: **{st.session_state.get('role_title', 'Target role')}** · Resume: **{st.session_state.get('resume_name', 'Uploaded resume')}**")

    a, b, c, d = st.columns(4)
    a.metric("Overall skill fit", f'{result["match_percentage"]:.0f}%')
    b.metric("Required skills", len(result["required_skills"]))
    c.metric("Matched skills", len(result["matched_skills"]))
    d.metric("Skills to build", len(result["missing_skills"]))

    st.progress(min(result["match_percentage"] / 100, 1.0))
    st.caption("Fit score combines explicit keyword matches and optional semantic similarity for supported skills. It is an estimate, not a hiring prediction.")

    overview_tab, detail_tab, plan_tab, report_tab = st.tabs(
        ["📊 Overview", "🧩 Skill evidence", "🛠 Learning plan", "📄 Export report"]
    )

    with overview_tab:
        left, right = st.columns([1, 1.2], gap="large")
        with left:
            st.markdown("#### Skill coverage")
            chart_df = pd.DataFrame({
                "Category": ["Matched", "Missing"],
                "Skills": [len(result["matched_skills"]), len(result["missing_skills"])],
            })
            fig = px.pie(chart_df, names="Category", values="Skills", hole=0.68,
                         color="Category", color_discrete_map={"Matched": "#16a34a", "Missing": "#f59e0b"})
            fig.update_layout(margin=dict(l=0, r=0, t=10, b=10), legend_title_text="", height=290)
            st.plotly_chart(fig, use_container_width=True)
        with right:
            st.markdown("#### Recommended focus")
            if recommendations:
                for item in recommendations[:4]:
                    st.markdown(f"**{item['skill']}** · {item['priority']} priority")
                    st.caption(item["suggestion"])
            else:
                st.success("All skills in the supported skill library were matched.")

    with detail_tab:
        st.markdown("#### Matching skills")
        if result["matched_skills"]:
            st.markdown("".join(f'<span class="skill-pill">✓ {s}</span>' for s in result["matched_skills"]), unsafe_allow_html=True)
        else:
            st.info("No supported required skills matched.")
        st.markdown("#### Skill gaps")
        if result["missing_skills"]:
            st.markdown("".join(f'<span class="missing-pill">＋ {s}</span>' for s in result["missing_skills"]), unsafe_allow_html=True)
        else:
            st.success("No supported skill gaps detected.")
        st.markdown("#### Evidence and match method")
        rows = []
        for skill in result["required_skills"]:
            evidence = result["skill_details"].get(skill, {})
            rows.append({
                "Required skill": skill,
                "Status": "Matched" if skill in result["matched_skills"] else "Gap",
                "Method": evidence.get("method", "Not matched"),
                "Similarity": f'{evidence.get("similarity", 0):.0%}' if evidence.get("similarity") is not None else "—",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.caption("Semantic matching can infer related wording, so review the evidence table and correct any false matches before relying on the result.")

    with plan_tab:
        st.markdown("#### A practical next-step plan")
        if recommendations:
            for idx, item in enumerate(recommendations, 1):
                with st.container(border=True):
                    st.markdown(f"**{idx}. {item['skill']}** · {item['priority']} priority")
                    st.write(item["suggestion"])
                    st.markdown(f"[Open learning resource ↗]({item['url']})")
        else:
            st.success("No gaps found in the supported skill list. Consider improving project evidence and documenting what you built.")
        st.info("Priorities are general guidance. Choose learning tasks based on your target role, interests, and current level.")

    with report_tab:
        st.write("Create a PDF summary of your match score, skill results, methods, and learning recommendations.")
        pdf_data = create_pdf_report(
            resume_name=st.session_state.get("resume_name", "resume"),
            role_title=st.session_state.get("role_title", "Target role"),
            result=result,
            recommendations=recommendations,
        )
        st.download_button("⬇ Download PDF report", data=pdf_data,
            file_name="skilllens_analysis_report.pdf", mime="application/pdf",
            type="primary", use_container_width=True)

st.divider()
st.markdown('<div class="small-muted">SkillLens · Educational project · Built with Python, Streamlit, NLP and semantic similarity</div>', unsafe_allow_html=True)
