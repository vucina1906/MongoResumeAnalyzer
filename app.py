from flask import Flask, request, render_template
import os
import pdfminer.high_level
import docx
import spacy
import re
import datetime
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB Connection (Replace with your connection string)
MONGO_URI = "YOUR_MONGODB_ATLAS_CONNECTION_STRING"
client = MongoClient(MONGO_URI)

# Databases & Collections
job_db = client["resume_analyzer"]
job_collection = job_db["jobs"]

user_db = client["resume_analyzer"]
resume_collection = user_db["resumes"]

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

nlp = spacy.load("en_core_web_sm")

# Sample Job Descriptions (If empty, add predefined jobs)
if job_collection.count_documents({}) == 0:
    job_collection.insert_many([
        {"title": "Data Scientist", "skills": ["Python", "Machine Learning", "NLP", "SQL"], "experience": 2},
        {"title": "Software Engineer", "skills": ["Python", "Django", "React", "MongoDB"], "experience": 3},
        {"title": "Data Analyst", "skills": ["SQL", "Power BI", "Excel", "Tableau"], "experience": 1}
    ])

def extract_text_from_pdf(pdf_path):
    try:
        return pdfminer.high_level.extract_text(pdf_path)
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"

def extract_text_from_docx(docx_path):
    try:
        doc = docx.Document(docx_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        return f"Error extracting text from DOCX: {str(e)}"

def extract_name(text):
    name_match = re.search(r"(?i)(?:Name[:\s-]+)([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)", text)
    if name_match:
        return name_match.group(1).strip()

    doc = nlp(text)
    possible_names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    return possible_names[0] if possible_names else ""

def extract_age(text):
    match = re.search(r'\b(\d{2})\s*(?:years? old|years|yrs|age)\b', text, re.IGNORECASE)
    return match.group(1) if match else ""

def extract_skills(text):
    skills_db = [
    # Programming Languages
    "Python", "Java", "C", "C++", "C#", "JavaScript", "TypeScript", "Swift", "Kotlin", "Go", "Rust", "R", "Julia", 
    "Perl", "Shell Scripting", "Scala",

    # Data Science & Machine Learning
    "Machine Learning", "Deep Learning", "Data Science", "Artificial Intelligence", "Computer Vision", "NLP", 
    "Time Series Analysis", "Recommendation Systems", "Anomaly Detection", "Predictive Analytics", "Reinforcement Learning",

    # Web Development & Frameworks
    "Flask", "Django", "FastAPI", "Spring Boot", "Node.js", "React", "Vue.js", "Angular", "Next.js", "ASP.NET", 
    "Bootstrap", "Tailwind CSS",

    # Databases
    "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Cassandra", "Firebase", "GraphQL", "Elasticsearch", "DynamoDB",
    
    # Big Data & ETL
    "Apache Spark", "Hadoop", "Kafka", "Airflow", "ETL Pipelines", "Databricks", "SSIS", "Google BigQuery", "Snowflake",
    
    # Cloud & DevOps
    "AWS", "Azure", "Google Cloud Platform (GCP)", "Cloud Computing", "Terraform", "Docker", "Kubernetes", "CI/CD", 
    "Jenkins", "GitHub Actions", "Ansible",

    # Data Visualization & BI Tools
    "Matplotlib", "Seaborn", "Plotly", "Tableau", "Power BI", "Looker", "D3.js", "Google Data Studio",
    
    # Libraries & Tools
    "Numpy", "Pandas", "Scikit-learn", "TensorFlow", "PyTorch", "OpenCV", "Statsmodels", "Tesseract", "Keras",
    "Shap", "LIME", "XGBoost", "LightGBM", "CatBoost", "Optuna", "Dask", "Hugging Face Transformers",
    
    # Software Development & Tools
    "Git", "GitHub", "Bitbucket", "JIRA", "Trello", "Confluence", "Agile", "Scrum", "Kanban",
    
    # Business Analytics & Experimentation
    "A/B Testing", "Hypothesis Testing", "Statistical Analysis", "Market Basket Analysis", "Churn Prediction",
    
    # Miscellaneous
    "Excel", "Google Sheets", "LaTeX", "Bash", "Regex", "Command Line", "Linux", "Cybersecurity", "Quantum Computing",
    
    # Soft Skills
    "Problem Solving", "Communication", "Critical Thinking", "Team Collaboration", "Presentation Skills", "Leadership"]
    return list(set(skill for skill in skills_db if skill.lower() in text.lower()))

def extract_experience(text):
    experience = re.findall(r'(\d+)\s*(?:years?|yrs?)\s*(?:experience|exp)', text, re.IGNORECASE)
    return max(map(int, experience), default=0)

def extract_education(text):
    education_patterns = [r"(Master(?:'s)?|Bachelor(?:'s)?|Ph\.?D|MBA|Doctorate|Diploma|Associate)\s+(?:of|in)?\s*([A-Za-z\s]+)"]
    return list(set([" ".join(match) for pattern in education_patterns for match in re.findall(pattern, text, re.IGNORECASE)]))

def extract_certifications(text):
    return re.findall(r'(certified|course|training)\s+[a-zA-Z\s]+', text, re.IGNORECASE)

def extract_location(text):
    countries = [
    # North America
    "United States", "Canada",
    # European Countries
    "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland",
    "France", "Germany", "Greece", "Hungary", "Ireland", "Italy", "Latvia", "Lithuania", "Luxembourg", "Malta",
    "Netherlands", "Poland", "Portugal", "Romania", "Slovakia", "Slovenia", "Spain", "Sweden","Albania", "Andorra", 
    "Belarus", "Bosnia and Herzegovina", "Georgia", "Iceland", "Liechtenstein","Moldova", "Monaco", "Montenegro", 
    "North Macedonia", "Norway", "San Marino", "Serbia", "Switzerland",
    "Ukraine", "United Kingdom", "Vatican City"
]
    return [country for country in countries if country.lower() in text.lower()]

def extract_phone(text):
    phone = re.findall(r"\+?\d{1,4}?\s?\(?\d{1,3}\)?\s?\d{1,4}\s?\d{1,4}\s?\d{1,4}", text)
    return phone[0] if phone else ""

def extract_email(text):
    email = re.findall(r"[\w\.-]+@[\w\.-]+", text)
    return email[0] if email else ""

def extract_soft_skills(text):
    soft_skills = ["communication", "leadership", "problem-solving", "teamwork"]
    return [skill for skill in soft_skills if skill in text.lower()]

def analyse_resume(text):
    return {
        "name": extract_name(text),
        "age": extract_age(text),
        "skills": extract_skills(text),
        "experience": extract_experience(text),
        "education": extract_education(text),
        "certifications": extract_certifications(text),
        "location": extract_location(text),
        "phone": extract_phone(text),
        "email": extract_email(text),
        "soft_skills": extract_soft_skills(text)
    }

def compare_with_jobs(resume_data):
    """Compares resume data with job descriptions and calculates match scores"""
    job_matches = []
    for job in job_collection.find():
        matched_skills = set(job["skills"]) & set(resume_data["skills"])
        skill_match_percentage = len(matched_skills) / len(job["skills"]) * 100 if job["skills"] else 0
        experience_match = (min(resume_data["experience"], job["experience"]) / job["experience"]) * 100 if job["experience"] else 0

        overall_score = round((skill_match_percentage * 0.7) + (experience_match * 0.3), 2)
        missing_skills = list(set(job["skills"]) - set(resume_data["skills"]))

        job_matches.append({
            "title": job["title"],
            "score": overall_score,
            "missing_skills": missing_skills
        })

    return sorted(job_matches, key=lambda x: x["score"], reverse=True)



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return 'No file uploaded', 400

    file = request.files['resume']
    if file.filename == '':
        return 'No file selected', 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    extracted_text = extract_text_from_pdf(file_path) if file.filename.endswith('.pdf') else extract_text_from_docx(file_path)
    analyzed_data = analyse_resume(extracted_text)

    return render_template("result.html", analysis=analyzed_data, matches=None)

@app.route('/submit', methods=['POST'])
def submit_resume():
    resume_data = {
        "name": request.form["name"],
        "age": request.form["age"],
        "skills": request.form["skills"].split(", "),
        "experience": int(request.form["experience"]),
        "education": request.form["education"].split(", "),
        "certifications": request.form["certifications"].split(", "),
        "location": request.form["location"].split(", "),
        "phone": request.form["phone"],
        "email": request.form["email"],
        "soft_skills": request.form["soft_skills"].split(", "),
        "submitted_at": datetime.datetime.utcnow()
    }

    resume_collection.insert_one(resume_data)

    job_matches = compare_with_jobs(resume_data)

    return render_template("result.html", analysis=resume_data, matches=job_matches)

@app.route('/query')
def query_page():
    """Render the query page with query buttons."""
    return render_template("query.html")

@app.route('/run_query', methods=['GET'])
def run_query():
    """Execute different queries based on user selection."""
    query_type = request.args.get("query")
    results = []

    if query_type == "top_skills":
        results = resume_collection.aggregate([
            {"$unwind": "$skills"},
            {"$group": {"_id": "$skills", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ])
        results = list(results)

    elif query_type == "high_experience":
        results = list(resume_collection.find({"experience": {"$gte": 5}}, {"_id": 0, "name": 1, "experience": 1}))

    elif query_type == "python_devs":
        results = list(resume_collection.find({"skills": {"$in": ["Python"]}}, {"_id": 0, "name": 1, "skills": 1}))

    elif query_type == "serbia_candidates":
        results = list(resume_collection.find({"location": {"$in": ["Serbia"]}}, {"_id": 0, "name": 1, "location": 1}))

    # ✅ Find resumes with multiple required skills (Python, SQL, Machine Learning)
    elif query_type == "multi_skill_candidates":
        required_skills = ["Python", "SQL", "Machine Learning"]
        results = list(resume_collection.find(
            {"skills": {"$all": required_skills}},  # Must contain ALL required skills
            {"_id": 0, "name": 1, "skills": 1}
        ))

    # ✅ Find resumes with at least 3 certifications
    elif query_type == "certified_candidates":
        results = list(resume_collection.find(
            {"certifications": {"$size": {"$gte": 3}}},  # Find resumes with 3 or more certifications
            {"_id": 0, "name": 1, "certifications": 1}
        ))

    # ✅ Find the most common locations among candidates
    elif query_type == "top_locations":
        results = resume_collection.aggregate([
            {"$unwind": "$location"},
            {"$group": {"_id": "$location", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ])
        results = list(results)

    # ✅ Find resumes that have at least 70% skill match with a predefined job
    elif query_type == "high_match_candidates":
        job_skills = ["Python", "Django", "SQL", "Machine Learning"]  # Example job skills
        results = resume_collection.aggregate([
            {
                "$project": {
                    "name": 1,
                    "skills": 1,
                    "matched_skills": {
                        "$setIntersection": ["$skills", job_skills]  # Find common skills
                    },
                    "total_skills": {"$size": "$skills"},
                    "matching_percentage": {
                        "$multiply": [
                            {"$divide": [{"$size": {"$setIntersection": ["$skills", job_skills]}}, len(job_skills)]},
                            100
                        ]
                    }
                }
            },
            {"$match": {"matching_percentage": {"$gte": 70}}},  # Only candidates with 70%+ match
            {"$sort": {"matching_percentage": -1}}
        ])
        results = list(results)

    # ✅ Find the average experience per skill
    elif query_type == "average_experience_per_skill":
        results = resume_collection.aggregate([
            {"$unwind": "$skills"},
            {"$group": {"_id": "$skills", "average_experience": {"$avg": "$experience"}}},
            {"$sort": {"average_experience": -1}}
        ])
        results = list(results)

    return render_template("query_results.html", results=results, query_type=query_type)



if __name__ == '__main__':
    app.run(debug=True)
