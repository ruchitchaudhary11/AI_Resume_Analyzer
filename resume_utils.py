from pypdf import PdfReader

from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_huggingface import HuggingFaceEmbeddings

from langchain_community.vectorstores import FAISS
from prompts import linkedin_jobs_prompt
from langchain_groq import ChatGroq
from prompts import (
    summary_prompt,
    strength_prompt,
    weakness_prompt,
    ats_prompt,
    jobs_prompt,
    interview_prompt
)

#Extract resume
def extract_text(uploaded_file):

    reader = PdfReader(uploaded_file)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:

            text += page_text

    return text

#Chunking the resume text
def create_chunks(text):

    splitter = RecursiveCharacterTextSplitter(

        chunk_size=700,

        chunk_overlap=200

    )

    return splitter.split_text(text)

#Create vector database from chunks
def create_vector_db(chunks):

    embedding_model = HuggingFaceEmbeddings(

        model_name="sentence-transformers/all-MiniLM-L6-v2"

    )

    vector_db = FAISS.from_texts(

        texts=chunks,

        embedding=embedding_model

    )

    return vector_db

#Groq model for analyzing the resume
def groq_llm(groq_api_key, vector_db, analyze):

    docs = vector_db.similarity_search(

        query=analyze,

        k=3

    )

    context = "\n\n".join(

        [doc.page_content for doc in docs]

    )

    llm = ChatGroq(

        groq_api_key=groq_api_key,

        model_name="openai/gpt-oss-20b",

        temperature=0

    )

    prompt = f"""

You are an Expert HR Recruiter.

Resume:

{context}

Task:

{analyze}

"""

    response = llm.invoke(prompt)

    return response.content

# Resume Summary
def analyze_summary(groq_api_key, vector_db, resume_text):

    prompt = summary_prompt(resume_text)

    return groq_llm(groq_api_key, vector_db, prompt)


# Resume Strength
def analyze_strength(groq_api_key, vector_db, resume_text):

    prompt = strength_prompt(resume_text)

    return groq_llm(groq_api_key, vector_db, prompt)


# Resume Weakness
def analyze_weakness(groq_api_key, vector_db, resume_text):

    prompt = weakness_prompt(resume_text)

    return groq_llm(groq_api_key, vector_db, prompt)


# ATS Score
def analyze_ats(groq_api_key, vector_db, resume_text):

    prompt = ats_prompt(resume_text)

    return groq_llm(groq_api_key, vector_db, prompt)


# Recommended Jobs
def analyze_jobs(groq_api_key, vector_db, resume_text):

    prompt = jobs_prompt(resume_text)

    return groq_llm(groq_api_key, vector_db, prompt)


# Interview Questions
def analyze_interview(groq_api_key, vector_db, resume_text):

    prompt = interview_prompt(resume_text)

    return groq_llm(groq_api_key, vector_db, prompt)

#Linkedin job

def extract_job_titles(groq_api_key, vector_db, resume_text):

    prompt = linkedin_jobs_prompt(resume_text)

    response = groq_llm(
        groq_api_key,
        vector_db,
        prompt
    )

    jobs = response.split("\n")

    return [job.strip() for job in jobs if job.strip()]