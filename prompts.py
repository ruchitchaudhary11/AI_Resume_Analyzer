"""
==========================================================
AI Resume Analyzer
Prompt Templates
==========================================================
"""


# ---------------------------------------------------------
# Resume Summary
# ---------------------------------------------------------
def summary_prompt(context):

    return f"""
You are an expert HR Recruiter and Resume Reviewer.

Analyze the following resume and generate a professional summary.

Resume:
-------------------------------------------------------
{context}
-------------------------------------------------------

Return the response in this format:

1. Candidate Overview
2. Education
3. Experience
4. Technical Skills
5. Projects
6. Achievements
7. Career Objective
8. Final Conclusion

Make the response professional and well formatted.
"""


# ---------------------------------------------------------
# Resume Strength
# ---------------------------------------------------------
def strength_prompt(context):

    return f"""
You are a professional HR Recruiter.

Analyze the resume below.

Resume:
-------------------------------------------------------
{context}
-------------------------------------------------------

Identify ONLY the strengths.

Return the response as bullet points.

Include:

• Technical Skills

• Projects

• Certifications

• Leadership

• Communication

• Problem Solving

• Overall Positive Impression

Do NOT mention weaknesses.
"""


# ---------------------------------------------------------
# Resume Weakness
# ---------------------------------------------------------
def weakness_prompt(context):

    return f"""
You are a professional HR Recruiter.

Analyze the following resume.

Resume:
-------------------------------------------------------
{context}
-------------------------------------------------------

Identify ONLY weaknesses.

Return bullet points.

Include:

• Missing Skills

• Weak Projects

• Missing Certifications

• ATS Problems

• Formatting Issues

• Grammar Issues

• Suggestions to improve

Do NOT repeat the summary.
"""


# ---------------------------------------------------------
# ATS Score
# ---------------------------------------------------------
def ats_prompt(context):

    return f"""
You are an ATS (Applicant Tracking System).

Evaluate the following resume.

Resume:
-------------------------------------------------------
{context}
-------------------------------------------------------

Return:

ATS Score : XX /100

Then explain

• Why?

• Missing Keywords

• Missing Skills

• ATS Friendly Suggestions

• Resume Improvement Tips
"""


# ---------------------------------------------------------
# Recommended Jobs
# ---------------------------------------------------------
def jobs_prompt(context):

    return f"""
You are an AI Career Advisor.

Analyze the following resume.

Resume:
-------------------------------------------------------
{context}
-------------------------------------------------------

Suggest Top 10 suitable job roles.

Return ONLY job titles.

Example:

Machine Learning Engineer

AI Engineer

Python Developer

Data Scientist

Backend Developer
"""


# ---------------------------------------------------------
# Interview Questions
# ---------------------------------------------------------
def interview_prompt(context):

    return f"""
You are a Senior Technical Interviewer.

Analyze the following resume.

Resume:
-------------------------------------------------------
{context}
-------------------------------------------------------

Generate 15 interview questions.

Include

Technical Questions

Project Questions

Behavioral Questions

HR Questions

Coding Questions
"""


# ---------------------------------------------------------
# Missing Skills
# ---------------------------------------------------------
def missing_skill_prompt(context):

    return f"""
Analyze the resume.

Resume:
-------------------------------------------------------
{context}
-------------------------------------------------------

List only missing skills.

Return bullet points.
"""


# ---------------------------------------------------------
# LinkedIn Headline
# ---------------------------------------------------------
def linkedin_headline_prompt(context):

    return f"""
Generate an attractive LinkedIn headline.

Resume:
-------------------------------------------------------
{context}
-------------------------------------------------------

Maximum 220 characters.
"""


# ---------------------------------------------------------
# Cover Letter
# ---------------------------------------------------------
def cover_letter_prompt(context, company_name, role):

    return f"""
Write a professional cover letter.

Company : {company_name}

Role : {role}

Resume:
-------------------------------------------------------
{context}
-------------------------------------------------------

Keep it professional.
"""


# ---------------------------------------------------------
# Skill Gap Analysis
# ---------------------------------------------------------
def skill_gap_prompt(resume, job_description):

    return f"""
Compare

Resume

-------------------------------------------------------
{resume}
-------------------------------------------------------

Job Description

-------------------------------------------------------
{job_description}
-------------------------------------------------------

Return

Match Percentage

Missing Skills

Important Keywords

Suggestions
"""
def linkedin_jobs_prompt(resume_text):

    return f"""
You are an Expert Career Advisor.

Analyze the following resume.

Extract ONLY the most suitable job titles.

Return maximum 5 job titles.

Output Example:

Python Developer
AI Engineer
Machine Learning Engineer
Data Scientist
Backend Developer

Resume:

{resume_text}
"""