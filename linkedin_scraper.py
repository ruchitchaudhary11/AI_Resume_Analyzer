import time
import numpy as np
import pandas as pd
import streamlit as st

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from streamlit_extras.add_vertical_space import add_vertical_space


class linkedin_scraper:

    # ============================================================
    # WEBDRIVER SETUP
    # ============================================================

    @staticmethod
    def webdriver_setup():

        options = webdriver.ChromeOptions()

        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")

        # Selenium Manager automatically finds the Chrome driver
        driver = webdriver.Chrome(
            options=options
        )

        driver.implicitly_wait(5)

        return driver


    # ============================================================
    # USER INPUT
    # ============================================================

    @staticmethod
    def get_userinput():

        add_vertical_space(2)

        with st.form(key="linkedin_scraper_form"):

            add_vertical_space(1)

            col1, col2, col3 = st.columns(
                [0.5, 0.3, 0.2],
                gap="medium"
            )

            # ----------------------------------------------------
            # Job Title
            # ----------------------------------------------------

            with col1:

                job_title_input = st.text_input(
                    label="Job Title",
                    placeholder="e.g. Java Developer"
                )

                # Convert comma-separated input into list
                job_title_input = [
                    x.strip()
                    for x in job_title_input.split(",")
                    if x.strip()
                ]

            # ----------------------------------------------------
            # Location
            # ----------------------------------------------------

            with col2:

                job_location = st.text_input(
                    label="Job Location",
                    value="India"
                )

            # ----------------------------------------------------
            # Number of Jobs
            # ----------------------------------------------------

            with col3:

                job_count = st.number_input(
                    label="Job Count",
                    min_value=1,
                    value=2,
                    step=1
                )

            add_vertical_space(1)

            submit = st.form_submit_button(
                label="Search Jobs"
            )

            add_vertical_space(1)

        return (
            job_title_input,
            job_location,
            int(job_count),
            submit
        )


    # ============================================================
    # BUILD LINKEDIN SEARCH URL
    # ============================================================

    @staticmethod
    def build_url(job_title, job_location):

        # --------------------------------------------------------
        # Convert job titles into LinkedIn search format
        # --------------------------------------------------------

        encoded_titles = []

        for title in job_title:

            title = title.strip()

            title = title.replace(" ", "%20")

            encoded_titles.append(title)

        keywords = "%2C%20".join(encoded_titles)

        location = job_location.strip().replace(
            " ",
            "%20"
        )

        # --------------------------------------------------------
        # LinkedIn public jobs search URL
        # --------------------------------------------------------

        link = (
            "https://www.linkedin.com/jobs/search/"
            f"?keywords={keywords}"
            f"&location={location}"
            "&f_TPR=r604800"
            "&position=1"
            "&pageNum=0"
        )

        return link


    # ============================================================
    # OPEN LINK
    # ============================================================

    @staticmethod
    def open_link(driver, link):

        try:

            driver.get(link)

            time.sleep(3)

            return True

        except Exception as e:

            st.error(
                f"Unable to open job page: {e}"
            )

            return False


    # ============================================================
    # OPEN SEARCH PAGE + LOAD JOBS
    # ============================================================

    @staticmethod
    def link_open_scrolldown(
        driver,
        link,
        job_count
    ):

        # --------------------------------------------------------
        # Open LinkedIn search page
        # --------------------------------------------------------

        success = linkedin_scraper.open_link(
            driver,
            link
        )

        if not success:
            return


        # --------------------------------------------------------
        # Give page time to load
        # --------------------------------------------------------

        time.sleep(3)


        # --------------------------------------------------------
        # Display basic debugging information
        # --------------------------------------------------------

        st.write(
            "Current URL:",
            driver.current_url
        )

        st.write(
            "Page title:",
            driver.title
        )


        # --------------------------------------------------------
        # Scroll multiple times
        #
        # We don't use job_count directly here because job_count
        # means number of jobs wanted, not number of scrolls.
        # --------------------------------------------------------

        scroll_count = max(
            3,
            min(job_count * 2, 10)
        )

        for _ in range(scroll_count):

            try:

                driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )

                time.sleep(1.5)

            except Exception:
                pass


        # --------------------------------------------------------
        # Try "See more jobs"
        # --------------------------------------------------------

        for _ in range(3):

            try:

                more_buttons = driver.find_elements(
                    By.XPATH,
                    "//button[contains(translate(., "
                    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
                    "'abcdefghijklmnopqrstuvwxyz'), "
                    "'see more jobs')]"
                )

                if more_buttons:

                    driver.execute_script(
                        "arguments[0].click();",
                        more_buttons[0]
                    )

                    time.sleep(2)

                else:

                    break

            except Exception:

                break


        # --------------------------------------------------------
        # Final scroll
        # --------------------------------------------------------

        try:

            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )

            time.sleep(2)

        except Exception:
            pass


    # ============================================================
    # JOB TITLE FILTER
    # ============================================================

    @staticmethod
    def job_title_filter(
        scraped_job_title,
        user_job_title_input
    ):

        if not scraped_job_title:
            return False

        scraped_title = (
            scraped_job_title
            .lower()
            .strip()
        )

        for user_title in user_job_title_input:

            user_title = (
                user_title
                .lower()
                .strip()
            )

            if not user_title:
                continue


            # ----------------------------------------------------
            # Exact phrase match
            # ----------------------------------------------------

            if user_title in scraped_title:
                return True


            # ----------------------------------------------------
            # Word-based match
            # ----------------------------------------------------

            words = user_title.split()

            if all(
                word in scraped_title
                for word in words
            ):
                return True


        return False


    # ============================================================
    # LOCATION FILTER
    # ============================================================

    @staticmethod
    def location_filter(
        scraped_location,
        requested_location
    ):

        if not scraped_location:
            return False

        if not requested_location:
            return True

        scraped_location = (
            scraped_location
            .lower()
            .strip()
        )

        requested_location = (
            requested_location
            .lower()
            .strip()
        )


        # --------------------------------------------------------
        # If user searches India, accept Indian locations
        # --------------------------------------------------------

        if requested_location == "india":

            return (
                "india" in scraped_location
                or
                "remote" in scraped_location
                or
                "hybrid" in scraped_location
            )


        # --------------------------------------------------------
        # Normal matching
        # --------------------------------------------------------

        if requested_location in scraped_location:
            return True


        if scraped_location in requested_location:
            return True


        # --------------------------------------------------------
        # Match individual location words
        # --------------------------------------------------------

        requested_words = requested_location.split()

        matched_words = sum(
            word in scraped_location
            for word in requested_words
        )

        return matched_words > 0


    # ============================================================
    # SCRAPE JOB DATA
    # ============================================================

    @staticmethod
    def scrap_company_data(
        driver,
        job_title_input,
        job_location
    ):

        jobs = []


        # ========================================================
        # FIND JOB CARDS
        # ========================================================

        cards = driver.find_elements(
            By.CSS_SELECTOR,
            "ul.jobs-search__results-list li"
        )


        # --------------------------------------------------------
        # Fallback selector
        # --------------------------------------------------------

        if not cards:

            cards = driver.find_elements(
                By.CSS_SELECTOR,
                ".jobs-search__results-list li"
            )


        # --------------------------------------------------------
        # Another fallback
        # --------------------------------------------------------

        if not cards:

            cards = driver.find_elements(
                By.CSS_SELECTOR,
                "li.base-card"
            )


        st.write(
            "Job cards found:",
            len(cards)
        )


        # ========================================================
        # IF NO CARDS FOUND
        # ========================================================

        if len(cards) == 0:

            st.warning(
                "No job cards were found on the LinkedIn page."
            )

            st.info(
                "The browser opened the page, but the expected "
                "job-card elements were not present."
            )

            return pd.DataFrame(
                columns=[
                    "Company Name",
                    "Job Title",
                    "Location",
                    "Website URL"
                ]
            )


        # ========================================================
        # PROCESS EACH JOB CARD
        # ========================================================

        for card in cards:

            try:

                # ------------------------------------------------
                # JOB TITLE
                # ------------------------------------------------

                title = ""

                title_selectors = [

                    ".base-search-card__title",

                    "h3.base-search-card__title",

                    "h3",

                    "a[href*='/jobs/view/']"
                ]


                for selector in title_selectors:

                    try:

                        element = card.find_element(
                            By.CSS_SELECTOR,
                            selector
                        )

                        title = element.text.strip()

                        if title:
                            break

                    except Exception:
                        continue


                # ------------------------------------------------
                # COMPANY
                # ------------------------------------------------

                company = ""

                company_selectors = [

                    ".base-search-card__subtitle",

                    "h4.base-search-card__subtitle",

                    "h4"
                ]


                for selector in company_selectors:

                    try:

                        element = card.find_element(
                            By.CSS_SELECTOR,
                            selector
                        )

                        company = element.text.strip()

                        if company:
                            break

                    except Exception:
                        continue


                # ------------------------------------------------
                # LOCATION
                # ------------------------------------------------

                location = ""

                location_selectors = [

                    ".job-search-card__location",

                    ".base-search-card__metadata",

                    "span"
                ]


                for selector in location_selectors:

                    try:

                        element = card.find_element(
                            By.CSS_SELECTOR,
                            selector
                        )

                        location = element.text.strip()

                        if location:
                            break

                    except Exception:
                        continue


                # ------------------------------------------------
                # JOB URL
                # ------------------------------------------------

                url = ""

                url_selectors = [

                    "a.base-card__full-link",

                    "a[href*='/jobs/view/']",

                    "a[href*='/jobs/']"
                ]


                for selector in url_selectors:

                    try:

                        element = card.find_element(
                            By.CSS_SELECTOR,
                            selector
                        )

                        url = element.get_attribute(
                            "href"
                        )

                        if url:
                            break

                    except Exception:
                        continue


                # ------------------------------------------------
                # Clean URL
                # ------------------------------------------------

                if url:

                    url = url.split("?")[0]


                # =================================================
                # VALIDATION
                # =================================================

                if not title:
                    continue

                if not company:
                    company = "Company Not Available"

                if not location:
                    location = "Location Not Available"


                # ------------------------------------------------
                # Job title filter
                # ------------------------------------------------

                title_match = linkedin_scraper.job_title_filter(
                    title,
                    job_title_input
                )


                if not title_match:
                    continue


                # ------------------------------------------------
                # Location filter
                # ------------------------------------------------

                location_match = linkedin_scraper.location_filter(
                    location,
                    job_location
                )


                if not location_match:
                    continue


                # ------------------------------------------------
                # Add job
                # ------------------------------------------------

                jobs.append({

                    "Company Name": company,

                    "Job Title": title,

                    "Location": location,

                    "Website URL": url

                })


            except Exception:

                # Skip malformed cards
                continue


        # ========================================================
        # CREATE DATAFRAME
        # ========================================================

        df = pd.DataFrame(
            jobs,
            columns=[
                "Company Name",
                "Job Title",
                "Location",
                "Website URL"
            ]
        )


        # ========================================================
        # REMOVE DUPLICATES
        # ========================================================

        if not df.empty:

            if "Website URL" in df.columns:

                df.drop_duplicates(
                    subset=["Website URL"],
                    inplace=True
                )

            else:

                df.drop_duplicates(
                    inplace=True
                )


            df.reset_index(
                drop=True,
                inplace=True
            )


        # ========================================================
        # DEBUG
        # ========================================================

        st.write(
            "Jobs after title/location filtering:",
            len(df)
        )


        return df


    # ============================================================
    # SCRAPE JOB DESCRIPTIONS
    # ============================================================

    @staticmethod
    def scrap_job_description(
        driver,
        df,
        job_count
    ):

        # --------------------------------------------------------
        # If dataframe is empty
        # --------------------------------------------------------

        if df.empty:

            return df


        # --------------------------------------------------------
        # Take requested number of jobs
        # --------------------------------------------------------

        df = df.head(
            int(job_count)
        ).copy()


        website_urls = df[
            "Website URL"
        ].tolist()


        job_descriptions = []


        # ========================================================
        # PROCESS EACH JOB
        # ========================================================

        for url in website_urls:

            description = (
                "Description Not Available"
            )


            # ----------------------------------------------------
            # Skip empty URL
            # ----------------------------------------------------

            if not url:

                job_descriptions.append(
                    description
                )

                continue


            try:

                # ------------------------------------------------
                # Open job
                # ------------------------------------------------

                success = linkedin_scraper.open_link(
                    driver,
                    url
                )


                if not success:

                    job_descriptions.append(
                        description
                    )

                    continue


                time.sleep(2)


                # ------------------------------------------------
                # Try multiple description selectors
                # ------------------------------------------------

                description_elements = []


                selectors = [

                    ".show-more-less-html__markup",

                    ".description__text",

                    ".jobs-description__content",

                    "div[class*='description']"
                ]


                for selector in selectors:

                    try:

                        elements = driver.find_elements(
                            By.CSS_SELECTOR,
                            selector
                        )

                        if elements:

                            description_elements = elements

                            break

                    except Exception:

                        continue


                # ------------------------------------------------
                # Extract description
                # ------------------------------------------------

                if description_elements:

                    text = description_elements[0].text.strip()

                    if text:

                        description = text


                # ------------------------------------------------
                # Try "Show more" if available
                # ------------------------------------------------

                if (
                    description
                    == "Description Not Available"
                ):

                    try:

                        show_more_buttons = driver.find_elements(
                            By.XPATH,
                            "//button[contains("
                            "translate(., "
                            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
                            "'abcdefghijklmnopqrstuvwxyz'), "
                            "'show more')]"
                        )


                        if show_more_buttons:

                            driver.execute_script(
                                "arguments[0].click();",
                                show_more_buttons[0]
                            )

                            time.sleep(1)


                            description_elements = driver.find_elements(
                                By.CSS_SELECTOR,
                                ".show-more-less-html__markup"
                            )


                            if description_elements:

                                text = (
                                    description_elements[0]
                                    .text
                                    .strip()
                                )

                                if text:

                                    description = text

                    except Exception:

                        pass


            except Exception:

                description = (
                    "Description Not Available"
                )


            job_descriptions.append(
                description
            )


        # ========================================================
        # ADD DESCRIPTION COLUMN
        # ========================================================

        df["Job Description"] = (
            job_descriptions
        )


        df.reset_index(
            drop=True,
            inplace=True
        )


        return df


    # ============================================================
    # DISPLAY RESULTS
    # ============================================================

    @staticmethod
    def display_data_userinterface(
        df_final
    ):

        add_vertical_space(1)


        # ========================================================
        # NO RESULTS
        # ========================================================

        if df_final.empty:

            st.markdown(
                """
                <h5 style="
                    text-align:center;
                    color:orange;
                ">
                    No Matching Jobs Found
                </h5>
                """,
                unsafe_allow_html=True
            )

            return


        # ========================================================
        # DISPLAY JOBS
        # ========================================================

        for i in range(
            len(df_final)
        ):

            st.markdown(
                f"""
                <h3 style="color:orange;">
                    Job Posting Details : {i + 1}
                </h3>
                """,
                unsafe_allow_html=True
            )


            # ----------------------------------------------------
            # Company
            # ----------------------------------------------------

            st.write(
                "Company Name :",
                df_final.iloc[i]["Company Name"]
            )


            # ----------------------------------------------------
            # Job title
            # ----------------------------------------------------

            st.write(
                "Job Title :",
                df_final.iloc[i]["Job Title"]
            )


            # ----------------------------------------------------
            # Location
            # ----------------------------------------------------

            st.write(
                "Location :",
                df_final.iloc[i]["Location"]
            )


            # ----------------------------------------------------
            # URL
            # ----------------------------------------------------

            st.write(
                "Website URL :",
                df_final.iloc[i]["Website URL"]
            )


            # ----------------------------------------------------
            # Description
            # ----------------------------------------------------

            with st.expander(
                "Job Description"
            ):

                st.write(
                    df_final.iloc[i][
                        "Job Description"
                    ]
                )


            add_vertical_space(3)


    # ============================================================
    # MAIN
    # ============================================================

    @staticmethod
    def main():

        driver = None


        try:

            # ----------------------------------------------------
            # Get user input
            # ----------------------------------------------------

            (
                job_title_input,
                job_location,
                job_count,
                submit
            ) = linkedin_scraper.get_userinput()


            add_vertical_space(2)


            # ====================================================
            # SUBMIT
            # ====================================================

            if submit:


                # ------------------------------------------------
                # Validate inputs
                # ------------------------------------------------

                if not job_title_input:

                    st.warning(
                        "Please enter a Job Title."
                    )

                    return


                if not job_location.strip():

                    st.warning(
                        "Please enter a Job Location."
                    )

                    return


                # =================================================
                # START DRIVER
                # =================================================

                with st.spinner(
                    "Chrome WebDriver setup..."
                ):

                    driver = (
                        linkedin_scraper
                        .webdriver_setup()
                    )


                # =================================================
                # BUILD SEARCH URL
                # =================================================

                link = (
                    linkedin_scraper
                    .build_url(
                        job_title_input,
                        job_location
                    )
                )


                # ------------------------------------------------
                # Show URL for debugging
                # ------------------------------------------------

                st.write(
                    "Search URL:",
                    link
                )


                # =================================================
                # LOAD JOB LISTINGS
                # =================================================

                with st.spinner(
                    "Loading job listings..."
                ):

                    linkedin_scraper.link_open_scrolldown(
                        driver,
                        link,
                        job_count
                    )


                # =================================================
                # SCRAPE JOB DATA
                # =================================================

                with st.spinner(
                    "Extracting job details..."
                ):

                    df = (
                        linkedin_scraper
                        .scrap_company_data(
                            driver,
                            job_title_input,
                            job_location
                        )
                    )


                # ------------------------------------------------
                # Show dataframe before descriptions
                # ------------------------------------------------

                if not df.empty:

                    st.write(
                        "Jobs found before descriptions:",
                        len(df)
                    )

                    st.dataframe(
                        df,
                        use_container_width=True
                    )


                # =================================================
                # SCRAPE DESCRIPTIONS
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
                # DISPLAY
                # =================================================

                linkedin_scraper.display_data_userinterface(
                    df_final
                )


        except Exception as e:

            st.error(
                f"Job search error: {e}"
            )


        finally:

            if driver is not None:

                try:

                    driver.quit()

                except Exception:

                    pass