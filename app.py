import streamlit as st

from linkedin_scraper import linkedin_scraper

from resume_utils import (
    extract_text,
    create_chunks,
    create_vector_db,
    analyze_summary,
    analyze_strength,
    analyze_weakness,
    analyze_ats,
    analyze_jobs,
    analyze_interview
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI Powered Resume Analyzer")
st.write("Upload your resume and analyze it using AI.")


# =========================================================
# SESSION STATE
# =========================================================

if "analyzed" not in st.session_state:
    st.session_state.analyzed = False


# =========================================================
# SIDEBAR
# =========================================================

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


# =========================================================
# UPLOAD RESUME
# =========================================================

uploaded_file = st.file_uploader(
    "Upload Resume (PDF)",
    type="pdf"
)


# =========================================================
# PROCESS RESUME
# =========================================================

if uploaded_file is not None:

    # Extract resume text
    resume_text = extract_text(uploaded_file)

    if not resume_text.strip():

        st.error(
            "Could not extract text from this PDF. "
            "Please upload a text-based PDF."
        )

    else:

        st.success("Resume Uploaded Successfully!")

        # -------------------------------------------------
        # Create Vector Database
        # -------------------------------------------------

        with st.spinner("Creating Resume Knowledge Base..."):

            chunks = create_chunks(resume_text)

            vector_db = create_vector_db(chunks)

        st.success("Knowledge Base Ready!")

        # -------------------------------------------------
        # Analyze Button
        # -------------------------------------------------

        if st.button("Analyze Resume"):

            st.session_state.analyzed = True

        # -------------------------------------------------
        # Run Analysis
        # -------------------------------------------------

        if st.session_state.analyzed:

            if not groq_api_key.strip():

                st.error("Please Enter Groq API Key")

            else:

                # =================================================
                # RESUME ANALYSIS
                # =================================================

                if analysis_option != "Recommended Jobs":

                    with st.spinner("Analyzing Resume..."):

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

                        elif analysis_option == "Interview Questions":

                            result = analyze_interview(
                                groq_api_key,
                                vector_db,
                                resume_text
                            )

                    st.markdown("---")
                    st.subheader("Result")
                    st.write(result)


                # =================================================
                # RECOMMENDED JOBS
                # =================================================

                else:

                    with st.spinner("Analyzing suitable job roles..."):

                        result = analyze_jobs(
                            groq_api_key,
                            vector_db,
                            resume_text
                        )

                    st.subheader("Recommended Jobs")
                    st.write(result)

                    st.markdown("---")

                    # =================================================
                    # LINKEDIN JOB SEARCH
                    # =================================================

                    st.subheader("🔎 Search LinkedIn Jobs")

                    (
                        job_title_input,
                        job_location,
                        job_count,
                        submit
                    ) = linkedin_scraper.get_userinput()

                    if submit:

                        driver = None

                        with st.spinner("Searching jobs..."):

                            try:

                                # -----------------------------------------
                                # Start Chrome
                                # -----------------------------------------

                                driver = linkedin_scraper.webdriver_setup()

                                # -----------------------------------------
                                # Build LinkedIn URL
                                # -----------------------------------------

                                link = linkedin_scraper.build_url(
                                    job_title_input,
                                    job_location
                                )

                                # Useful debugging information
                                st.info(
                                    f"Searching for: "
                                    f"{', '.join(job_title_input)} "
                                    f"in {job_location}"
                                )

                                # -----------------------------------------
                                # Open LinkedIn Jobs
                                # -----------------------------------------

                                linkedin_scraper.link_open_scrolldown(
                                    driver,
                                    link,
                                    job_count
                                )

                                # -----------------------------------------
                                # Scrape Job Cards
                                # -----------------------------------------

                                df = linkedin_scraper.scrap_company_data(
                                    driver,
                                    job_title_input,
                                    job_location,
                                    job_count
                                )

                                # -----------------------------------------
                                # Display Result
                                # -----------------------------------------

                                if df is not None and not df.empty:

                                    st.success(
                                        f"Found {len(df)} matching jobs."
                                    )

                                    linkedin_scraper.display_data_userinterface(
                                        df
                                    )

                                else:

                                    st.warning(
                                        "No matching jobs found."
                                    )

                                    # Debug information
                                    st.write(
                                        "**Current URL:**",
                                        driver.current_url
                                    )

                                    st.write(
                                        "**Page Title:**",
                                        driver.title
                                    )

                            except Exception as e:

                                st.error(
                                    f"LinkedIn scraping error: {str(e)}"
                                )

                            finally:

                                if driver is not None:

                                    driver.quit()