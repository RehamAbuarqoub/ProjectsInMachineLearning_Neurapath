import os
from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import docx2txt
import PyPDF2
import re

from utils.semantic_matcher import SemanticSkillMatcher

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'my-very-secret-key'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ---------- Load Dataset ----------
JOBS_DF = pd.read_csv('data/job_skill_data.csv').dropna(subset=['job_title', 'company', 'job_location', 'job_skills'])
JOB_OPTIONS = JOBS_DF.apply(lambda row: f"{row['job_title']} | {row['company']} | {row['job_location']}", axis=1).tolist()

# ---------- AI Semantic Matcher ----------
matcher = SemanticSkillMatcher(model_name='all-MiniLM-L6-v2', threshold=0.7)

# ---------- Helpers ----------
def extract_text_from_resume(filepath):
    if filepath.endswith('.pdf'):
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ''.join([page.extract_text() or '' for page in reader.pages])
        return text
    elif filepath.endswith('.docx'):
        return docx2txt.process(filepath)
    return ""

def extract_skills_from_text(text, all_possible_skills):
    # Very basic, just use comma/newline/semicolon split; can be improved with spaCy NER
    text = text.replace(';', ',').replace('\n', ',')
    tokens = [s.strip() for s in text.split(',') if s.strip()]
    # Deduplicate and preserve order
    seen = set()
    skills = []
    for t in tokens:
        title = t.title()
        if title not in seen:
            skills.append(title)
            seen.add(title)
    return skills

def calculate_fit_score(matched, required):
    if not required:
        return 0
    return round(len(matched) / len(required), 2)

def get_best_matches_with_skills(user_skills, jobs_df, matcher, threshold=0.5, exclude_idx=None):
    results = []
    for idx, row in jobs_df.iterrows():
        if exclude_idx is not None and idx == exclude_idx:
            continue
        job_skills = [s.strip().title() for s in str(row['job_skills']).split(',') if s.strip()]
        matched, _ = matcher.match(user_skills, job_skills)
        score = calculate_fit_score(matched, job_skills)
        results.append((idx, score, matched))
    # Only return jobs with fit score > threshold
    results = [x for x in results if x[1] > threshold]
    results.sort(key=lambda x: x[1], reverse=True)
    return [
        jobs_df.iloc[i].to_dict() | {
            'fit_score': score,
            'matched_skills': matched
        }
        for i, score, matched in results
    ]

# ---------- Routes ----------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'user' and password == 'pass':
            session['user'] = username
            return redirect(url_for('analyze'))
        else:
            error = "Invalid username or password."
    return render_template('login.html', error=error)

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    if 'user' not in session:
        return redirect(url_for('login'))
    error = None
    result = None
    if request.method == 'POST':
        job_idx = int(request.form['job_idx'])
        job_row = JOBS_DF.iloc[job_idx]
        job_skills = [s.strip().title() for s in str(job_row['job_skills']).split(',') if s.strip()]
        all_skills = set()
        for skills in JOBS_DF['job_skills']:
            for s in str(skills).split(','):
                all_skills.add(s.strip().title())
        file = request.files['resume']
        if file and file.filename:
            ext = os.path.splitext(file.filename)[-1].lower()
            filename = f"resume_{job_idx}{ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            resume_text = extract_text_from_resume(filepath)
            user_skills = extract_skills_from_text(resume_text, all_skills)
            matched, missing = matcher.match(user_skills, job_skills)
            fit_score = calculate_fit_score(matched, job_skills)

            # Show ALL jobs with fit score > 50%
            best_jobs = get_best_matches_with_skills(user_skills, JOBS_DF, matcher, threshold=0.5, exclude_idx=job_idx)
            show_selected = fit_score >= 0.5

            job_summary = job_row['job_summary'] if isinstance(job_row['job_summary'], str) else ""
            job_summary = (job_summary[:350] + '...') if job_summary else ""
            result = {
                'fit_score': int(fit_score * 100),
                'matched_skills': matched,
                'missing_skills': missing,
                'job_title': job_row['job_title'],
                'company': job_row['company'],
                'job_location': job_row['job_location'],
                'job_summary': job_summary,
                'best_jobs': best_jobs,
                'show_selected': show_selected,
                'reason_unmatched': None
            }
            if not show_selected:
                result['reason_unmatched'] = (
                    f"Your resume does not match enough required skills for the job: "
                    f"{job_row['job_title']} at {job_row['company']} ({job_row['job_location']}). "
                    f"Your fit score is {int(fit_score * 100)}%."
                )
            return render_template('result.html', **result)
        else:
            error = "Please upload a resume file (.pdf or .docx)."

    return render_template('analyze.html', job_options=enumerate(JOB_OPTIONS), error=error)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
            