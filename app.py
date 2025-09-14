import streamlit as st
import pdfplumber
import docx2txt
import spacy

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Define a sample skills database
skills_db = ["Python", "Java", "C++", "SQL", "Machine Learning", "Deep Learning", "AWS", "Git", "Linux"]

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file):
    return docx2txt.process(file)

def extract_skills(text):
    doc = nlp(text)
    found_skills = set()
    for token in doc:
        if token.text in skills_db:
            found_skills.add(token.text)
    return list(found_skills)

def parse_job_description(jd_text):
    jd_skills = []
    for skill in skills_db:
        if skill.lower() in jd_text.lower():
            jd_skills.append(skill)
    return jd_skills

def match_resume(resume_skills, job_skills):
    matched = set(resume_skills) & set(job_skills)
    missing = set(job_skills) - set(resume_skills)
    score = (len(matched) / len(job_skills)) * 100 if job_skills else 0
    return matched, missing, score

# --- Streamlit UI ---
st.title("📄 Resume Parser + Job Matcher")

uploaded_file = st.file_uploader("Upload your Resume (PDF/DOCX)", type=["pdf", "docx"])
job_description = st.text_area("Paste the Job Description here:")

if uploaded_file and job_description:
    # Extract text
    if uploaded_file.type == "application/pdf":
        resume_text = extract_text_from_pdf(uploaded_file)
    else:
        resume_text = extract_text_from_docx(uploaded_file)

    # Extract skills
    resume_skills = extract_skills(resume_text)
    job_skills = parse_job_description(job_description)

    # Match
    matched, missing, score = match_resume(resume_skills, job_skills)

    # Show results
    st.subheader("🔍 Results")
    st.write("**Resume Skills:**", resume_skills)
    st.write("**Job Skills:**", job_skills)
    st.write("✅ Matched Skills:", list(matched))
    st.write("❌ Missing Skills:", list(missing))
    st.write(f"📊 Match Score: **{score:.2f}%**")

