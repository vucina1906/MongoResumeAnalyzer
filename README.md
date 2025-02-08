This is ResumeMatch AI, a Flask-based app that analyze resumes and match them with job descriptions using MongoDB and NLP. It automatically extracts skills, experience, and certifications from resumes, compares them with job requirements, and provides suggestions for improvement.This project also includes advanced predefined queries, allowing recruiters and candidates to search resumes by skills, experience, location, and more with just one click.

App features: 

- Upload Resume & Auto-Fill Fields → Upload a PDF/DOCX resume, and the app will extract name, skills, experience, education, certifications, and contact info automatically.

- Manual Editing Before Submission → Users can edit or add missing details before submitting their resume.

- Job Matching & Skill Comparison → The app compares the extracted skills and experience with predefined job descriptions and generates a match score. 

- Predefined One-Click Queries → Easily search the resume database with predefined filters:
🔹 Find top 5 most common skills
🔹 Filter resumes by skills, experience, and location
🔹 Identify candidates with 70%+ job match
🔹 Find candidates with multiple certifications
🔹 Analyze average experience per skill

- Resume & Job Storage in MongoDB → Resumes are stored in MongoDB Atlas, making them searchable via MongoDB Compass or mongosh.

- Modern UI with Bootstrap → A clean and responsive Bootstrap-based design with a custom background image (image.jpg). 

- Cloud-Hosted MongoDB Atlas Database → Access data from anywhere and query resumes remotely. 

How to use: 

1. Clone the Repository 

2. Install Dependencies 

3. Set Up MongoDB Atlas 
- Replace YOUR_MONGODB_ATLAS_CONNECTION_STRING in app.py with your actual connection string. So it should be in down bellow format
mongodb+srv://vucina19931906:**********@cluster0.idbyw.mongodb.net/resume_analyzer?retryWrites=true&w=majority , 
instead vucina19931906:**********@ it will be your username and password mongodb will create for you the rest is the same. 

4. Run the App

-------------------------------- 

You can also customize the app.py file to change the sample job descriptions (predefined jobs), the skills database, and the list of countries to better fit your needs. 




