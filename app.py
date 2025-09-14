# app.py -- lightweight Resume Parser + Job Matcher (no spaCy)
import streamlit as st
import pdfplumber
from docx import Document
from io import BytesIO
import re
import json

st.set_page_config(page_title="Resume Parser + Job Matcher", layout="wide")
st.title("📄 Resume Parser + Job Matcher (lightweight)")

skills_db = [
    "Python","Java","C++","C","SQL","NoSQL","JavaScript","TypeScript","HTML","CSS",
    "Machine Learning","Deep Learning","TensorFlow","PyTorch","Pandas","NumPy",
    "AWS","Azure","GCP","Docker","Kubernetes","Git","Linux","REST","GraphQL",
    "React","Vue","Angular","Django","Flask","FastAPI","CI/CD","Jenkins","Terraform"
]

def extract_text_from_pdf(uploaded_file):
    uploaded_file.seek(0)
    data = uploaded_file.read()
    text = ""
    with pdfplumber.open(BytesIO(data)) as pdf:
        for p in pdf.pages:
            page_text = p.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_text_from_docx(uploaded_file):
    uploaded_file.seek(0)
    data = uploaded_file.read()
    doc = Document(BytesIO(data))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)

def extract_skills(text, skills_db):
    text_lower = text.lower()
    found = set()

    for skill in skills_db:
        if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text_lower):
            found.add(skill)

    lines = text.splitlines()
    for i, line in enumerate(lines):
        if 'skill' in line.lower():
            block = " ".join(lines[i:i+6])
            tokens = re.split(r'[,\u2022;•\n\-–—]', block)
            for tok in tokens:
                tok = tok.strip()
                for skill in skills_db:
                    if skill.lower() in tok.lower():
                        found.add(skill)
    return sorted(found)

def parse_job_description(jd_text, skills_db):
    return extract_skills(jd_text, skills_db)

def match_resume(resume_skills, job_skills):
    matched = sorted(set(resume_skills) & set(job_skills))
    missing = sorted(set(job_skills) - set(resume_skills))
    score = (len(matched) / len(job_skills) * 100) if job_skills else 0.0
    return matched, missing, score

uploaded_file = st.file_uploader("Upload your Resume (PDF or DOCX)", type=["pdf","docx"])
job_description = st.text_area("Paste the Job Description (required)", height=200)

if st.button("Run match"):
    if not uploaded_file:
        st.error("Please upload a resume file (PDF or DOCX).")
    elif not job_description.strip():
        st.error("Please paste the job description.")
    else:
        try:
            if uploaded_file.type == "application/pdf" or uploaded_file.name.lower().endswith(".pdf"):
                resume_text = extract_text_from_pdf(uploaded_file)
            else:
                resume_text = extract_text_from_docx(uploaded_file)
        except Exception as e:
            st.error(f"Failed to read resume: {e}")
            raise

        resume_skills = extract_skills(resume_text, skills_db)
        job_skills = parse_job_description(job_description, skills_db)
        matched, missing, score = match_resume(resume_skills, job_skills)

        st.subheader("🔍 Results")
        st.write("**Resume Skills (detected):**", resume_skills)
        st.write("**Job Skills (detected from JD):**", job_skills)
        st.write("✅ Matched:", matched)
        st.write("❌ Missing:", missing)
        st.write(f"📊 Match score: **{score:.1f}%**")

        result = {"resume_skills": resume_skills, "job_skills": job_skills,
                  "matched": matched, "missing": missing, "score": score}
        st.download_button("Download JSON result", data=json.dumps(result, indent=2), file_name="match_result.json")
