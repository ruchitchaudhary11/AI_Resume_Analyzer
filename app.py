import streamlit as st
from pypdf import PdfReader
from linkedin_scraper import linkedin_scraper
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from resume_utils import (
    analyze_summary,
    analyze_strength,
    analyze_weakness,
    analyze_ats,
    analyze_jobs,
    analyze_interview
)

# ---------------------------
# Page Config
# ---------------------------

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI Powered Resume Analyzer")
st.write("Upload your resume and analyze it using AI.")
if "analyzed" not in st.session_state:
    st.session_state.analyzed = False

# ---------------------------
# Sidebar
# ---------------------------

groq_api_key = st.sidebar.text_input(
    "Groq API Key",
    type="password"
)

analysis_option = st.sidebar.selectbox(
    "Choose Analysis",
    [
        "Resume Summary",
        "Resume Strength",
        "Resume Weakness",
        "ATS Score",
        "Recommended Jobs",
        "Interview Questions"
    ]
)
    

# ---------------------------
# Upload Resume
# ---------------------------

uploaded_file = st.file_uploader(
    "Upload Resume (PDF)",
    type="pdf"
)

# ---------------------------
# Process Resume
# ---------------------------

if uploaded_file is not None:

    reader = PdfReader(uploaded_file)

    resume_text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:

            resume_text += page_text

    st.success("Resume Uploaded Successfully!")

    with st.spinner("Creating Embeddings..."):

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100
        )

        chunks = splitter.split_text(resume_text)

        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        vector_db = FAISS.from_texts(
            chunks,
            embedding_model
        )

    st.success("Knowledge Base Ready!")

    # -----------------------
    # Analyze Button
    # -----------------------

    if st.button("Analyze Resume"):
        st.session_state.analyzed=True
    if st.session_state.analyzed:

        if groq_api_key == "":

            st.error("Please Enter Groq API Key")

        else:

            with st.spinner("Analyzing..."):

                if analysis_option == "Resume Summary":

                    result = analyze_summary(
                        groq_api_key,
                        vector_db,
                        resume_text
                    )

                elif analysis_option == "Resume Strength":

                    result = analyze_strength(
                        groq_api_key,
                        vector_db,
                        resume_text
                    )

                elif analysis_option == "Interview Questions":
                
                    result = analyze_interview(
                        groq_api_key,
                        vector_db,
                        resume_text
                    )

                elif analysis_option == "Resume Weakness":

                    result = analyze_weakness(
                        groq_api_key,
                        vector_db,
                        resume_text
                    )
                elif analysis_option == "ATS Score":
                    
                    result = analyze_ats(
                        groq_api_key,
                        vector_db,
                        resume_text
                    )

                elif analysis_option == "Recommended Jobs":

                    result = analyze_jobs(
                        groq_api_key,
                        vector_db,
                        resume_text
                    )

                    st.subheader("Recommended Jobs")
                    st.write(result)
                    st.markdown("---")

                    #user input
                    job_title_input,job_location,job_count,submit=linkedin_scraper.get_userinput()
                    if submit:
                        with st.spinner("Searching jobs.."):
                            driver=None

                            try:
                                driver=linkedin_scraper.webdriver_setup()

                                link=linkedin_scraper.build_url(
                                    job_title_input,
                                    job_location
                                )
                                # st.write("Job Title Input:", job_title_input)
                                # st.write("Generated URL:", link)

                                linkedin_scraper.link_open_scrolldown(
                                    driver,
                                    link,
                                    job_count
                                )
                                # st.write("Current URL:", driver.current_url)
                                # st.write("Page Title:", driver.title)
                                df=linkedin_scraper.scrap_company_data(
                                    driver,
                                    job_title_input,
                                    job_location,
                                    job_count
                                )

                                if len(df)>0:
                                    linkedin_scraper.display_data_userinterface(df)
                                else:
                                    st.warning("No matching jobs found.")
                                
                            except Exception as e:
                                st.error(f"Error:{e}")

                            finally:
                                if driver:
                                    driver.quit()
                            

                if analysis_option!="Recommended Jobs":
                    st.markdown("---")
                    st.subheader("Result")
                    st.write(result)

                   