# 🤖 AI Resume Analyzer & LinkedIn Job Scraper

An AI-powered Streamlit application that analyzes resumes using
Generative AI and helps users discover relevant LinkedIn job
opportunities.

## 🚀 Features

-   📄 Upload and analyze PDF resumes
-   📝 AI-generated Resume Summary
-   💪 Resume Strength & Weakness Analysis
-   🎯 AI-based ATS Score
-   💼 Recommended Job Roles
-   🎤 AI-generated Interview Questions
-   🔎 LinkedIn Job Search using Selenium
-   🃏 Extract Job Title, Company, Location & URL
-   📋 Extract Job Descriptions
-   🧠 RAG-based resume analysis using FAISS
-   💬 Groq LLM integration

## 🛠️ Tech Stack

-   **Python**
-   **Streamlit**
-   **LangChain**
-   **FAISS**
-   **Hugging Face Embeddings**
-   **Groq LLM**
-   **Selenium**
-   **Pandas & NumPy**
-   **PyPDF**

## 🧠 Architecture

``` text
Resume PDF
    ↓
Text Extraction
    ↓
Text Chunking
    ↓
Hugging Face Embeddings
    ↓
FAISS Vector Database
    ↓
Relevant Resume Context
    ↓
Groq LLM
    ↓
AI Analysis
```

### LinkedIn Scraping

``` text
Job Title + Location + Job Count
              ↓
      LinkedIn Search URL
              ↓
       Selenium WebDriver
              ↓
        Open LinkedIn
              ↓
       Scroll & Load Jobs
              ↓
         Job Cards
              ↓
   Extract Job Information
              ↓
 Job Title | Company | Location | URL
              ↓
      Open Job Posting URLs
              ↓
      Extract Job Description
```

### 🔎 LinkedIn Scraping Details

The LinkedIn scraper is implemented using **Selenium WebDriver**.

The user provides:

-   **Job Title** --- e.g. `Data Analyst`
-   **Job Location** --- e.g. `India`
-   **Job Count** --- number of jobs to fetch

The application builds the LinkedIn search URL and Selenium opens it in
the browser.

The scraper then:

1.  Opens LinkedIn using Selenium.
2.  Navigates to the generated job-search URL.
3.  Scrolls the page to load job listings.
4.  Detects LinkedIn job cards using CSS selectors.
5.  Extracts:
    -   Company Name
    -   Job Title
    -   Location
    -   Job URL
6.  Opens individual job URLs.
7.  Extracts the Job Description.
8.  Stores the results in a Pandas DataFrame.
9.  Displays the job postings in Streamlit.

Example extracted data:

``` text
Company Name     → ABC Company
Job Title        → Data Analyst
Location         → India
Website URL      → LinkedIn Job URL
Job Description  → Complete job description
```

This job-description data can also be used in future versions for
**Resume vs Job Description matching** and calculating a personalized
job-fit score.

## 📁 Project Structure

``` text
AI-Resume-Analyzer/
│
├── app.py
├── linkedin_scraper.py
├── resume_utils.py
├── prompts.py
├── requirements.txt
└── README.md
```

## ⚙️ Installation

``` bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
```

## 🔑 API Key

Enter your **Groq API Key** through the Streamlit sidebar.

Do not commit API keys to GitHub.

## ▶️ Run

``` bash
streamlit run app.py
```

Open:

``` text
http://localhost:8501
```

## 🔍 How It Works

### Resume Analysis

1.  Upload your resume.
2.  Resume text is extracted from the PDF.
3.  Text is split into chunks.
4.  Chunks are converted into embeddings.
5.  FAISS stores the embeddings.
6.  Relevant resume context is retrieved.
7.  Groq LLM generates the selected analysis.

### Job Search

1.  Select **Recommended Jobs**.
2.  Enter Job Title, Location and Job Count.
3.  Selenium opens LinkedIn.
4.  Jobs are loaded through scrolling.
5.  Job cards are scraped.
6.  Job descriptions are extracted.
7.  Results are displayed in Streamlit.

## 🔮 Future Enhancements

-   🎯 Resume vs Job Description Match Score
-   🤖 AI Career Chatbot
-   🎤 AI Mock Interview
-   📚 Personalized Learning Roadmap
-   📋 Job Application Tracker
-   🧩 Skill Gap Analysis
-   📊 Job Fit Score based on resume and job description

## ⚠️ Limitations

-   LinkedIn can change its page structure and CSS selectors.
-   Selenium-based scraping may require browser/driver configuration.
-   Cloud deployment requires a compatible headless browser setup.
-   ATS score is an AI-based estimate and may differ from a company's
    actual ATS.

## 👨‍💻 Author

**Ruchit Chaudhary**

B.Tech --- Artificial Intelligence
