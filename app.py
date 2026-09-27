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


# =========================================================
# MAIN TITLE
# =========================================================

st.title("📄 AI Powered Resume Analyzer")

st.write(
    "Upload your resume and analyze it using AI."
)


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

    # -----------------------------------------------------
    # Extract resume text
    # -----------------------------------------------------

    resume_text = extract_text(
        uploaded_file
    )

    if not resume_text.strip():

        st.error(
            "Could not extract text from this PDF. "
            "Please upload a text-based PDF."
        )

    else:

        st.success(
            "Resume Uploaded Successfully!"
        )

        # -------------------------------------------------
        # Create Resume Knowledge Base
        # -------------------------------------------------

        with st.spinner(
            "Creating Resume Knowledge Base..."
        ):

            chunks = create_chunks(
                resume_text
            )

            vector_db = create_vector_db(
                chunks
            )

        st.success(
            "Knowledge Base Ready!"
        )

        # -------------------------------------------------
        # Analyze Button
        # -------------------------------------------------

        if st.button(
            "Analyze Resume"
        ):

            st.session_state.analyzed = True

        # -------------------------------------------------
        # Run Analysis
        # -------------------------------------------------

        if st.session_state.analyzed:

            # =================================================
            # CHECK GROQ API KEY
            # =================================================

            if not groq_api_key.strip():

                st.error(
                    "Please Enter Groq API Key"
                )

            else:

                # =================================================
                # NORMAL RESUME ANALYSIS
                # =================================================

                if analysis_option != "Recommended Jobs":

                    with st.spinner(
                        "Analyzing Resume..."
                    ):

                        # -----------------------------------------
                        # Resume Summary
                        # -----------------------------------------

                        if analysis_option == "Resume Summary":

                            result = analyze_summary(
                                groq_api_key,
                                vector_db,
                                resume_text
                            )

                        # -----------------------------------------
                        # Resume Strength
                        # -----------------------------------------

                        elif analysis_option == "Resume Strength":

                            result = analyze_strength(
                                groq_api_key,
                                vector_db,
                                resume_text
                            )

                        # -----------------------------------------
                        # Resume Weakness
                        # -----------------------------------------

                        elif analysis_option == "Resume Weakness":

                            result = analyze_weakness(
                                groq_api_key,
                                vector_db,
                                resume_text
                            )

                        # -----------------------------------------
                        # ATS Score
                        # -----------------------------------------

                        elif analysis_option == "ATS Score":

                            result = analyze_ats(
                                groq_api_key,
                                vector_db,
                                resume_text
                            )

                        # -----------------------------------------
                        # Interview Questions
                        # -----------------------------------------

                        elif analysis_option == "Interview Questions":

                            result = analyze_interview(
                                groq_api_key,
                                vector_db,
                                resume_text
                            )

                    # -----------------------------------------
                    # Display Result
                    # -----------------------------------------

                    st.markdown("---")

                    st.subheader(
                        "Result"
                    )

                    st.write(
                        result
                    )


                # =================================================
                # RECOMMENDED JOBS
                # =================================================

                else:

                    # -----------------------------------------
                    # AI Recommended Jobs
                    # -----------------------------------------

                    with st.spinner(
                        "Analyzing suitable job roles..."
                    ):

                        result = analyze_jobs(
                            groq_api_key,
                            vector_db,
                            resume_text
                        )

                    st.subheader(
                        "Recommended Jobs"
                    )

                    st.write(
                        result
                    )

                    st.markdown("---")


                    # =================================================
                    # LINKEDIN JOB SEARCH
                    # =================================================

                    st.subheader(
                        "🔎 Search LinkedIn Jobs"
                    )


                    # -------------------------------------------------
                    # Get LinkedIn User Input
                    # -------------------------------------------------

                    (
                        job_title_input,
                        job_location,
                        job_count,
                        submit
                    ) = linkedin_scraper.get_userinput()


                    # =================================================
                    # SEARCH BUTTON
                    # =================================================

                    if submit:

                        driver = None

                        try:

                            # -----------------------------------------
                            # Start Chrome WebDriver
                            # -----------------------------------------

                            with st.spinner(
                                "Starting Chrome WebDriver..."
                            ):

                                driver = (
                                    linkedin_scraper
                                    .webdriver_setup()
                                )


                            # -----------------------------------------
                            # Build LinkedIn Search URL
                            # -----------------------------------------

                            link = (
                                linkedin_scraper
                                .build_url(
                                    job_title_input,
                                    job_location
                                )
                            )


                            # -----------------------------------------
                            # Search Information
                            # -----------------------------------------

                            st.info(
                                f"Searching for: "
                                f"{', '.join(job_title_input)} "
                                f"in {job_location}"
                            )


                            # -----------------------------------------
                            # Open LinkedIn Jobs
                            # -----------------------------------------

                            with st.spinner(
                                "Loading LinkedIn jobs..."
                            ):

                                linkedin_scraper.link_open_scrolldown(
                                    driver,
                                    link,
                                    job_count
                                )


                            # -----------------------------------------
                            # Scrape Job Cards
                            # -----------------------------------------

                            with st.spinner(
                                "Extracting job details..."
                            ):

                                df = (
                                    linkedin_scraper
                                    .scrap_company_data(
                                        driver,
                                        job_title_input,
                                        job_location,
                                        job_count
                                    )
                                )


                            # =================================================
                            # CHECK JOB RESULTS
                            # =================================================

                            if df is None or df.empty:

                                st.warning(
                                    "No matching jobs found."
                                )

                                # -----------------------------------------
                                # Debug information
                                # -----------------------------------------

                                st.write(
                                    "**Current URL:**",
                                    driver.current_url
                                )

                                st.write(
                                    "**Page Title:**",
                                    driver.title
                                )


                            else:

                                st.success(
                                    f"Found {len(df)} "
                                    f"matching jobs."
                                )


                                # =================================================
                                # SCRAPE JOB DESCRIPTIONS
                                # =================================================

                                with st.spinner(
                                    "Loading job descriptions..."
                                ):

                                    df_final = (
                                        linkedin_scraper
                                        .scrap_job_description(
                                            driver,
                                            df,
                                            job_count
                                        )
                                    )


                                # =================================================
                                # DISPLAY FINAL RESULTS
                                # =================================================

                                st.markdown("---")

                                st.subheader(
                                    "💼 LinkedIn Job Results"
                                )


                                linkedin_scraper.display_data_userinterface(
                                    df_final
                                )


                        # =================================================
                        # ERROR HANDLING
                        # =================================================

                        except Exception as e:

                            st.error(
                                f"LinkedIn scraping error: {str(e)}"
                            )


                        # =================================================
                        # CLOSE DRIVER
                        # =================================================

                        finally:

                            if driver is not None:

                                try:

                                    driver.quit()

                                except Exception:

                                    pass