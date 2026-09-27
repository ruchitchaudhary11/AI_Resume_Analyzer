import time
import numpy as np
import pandas as pd
import streamlit as st

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from streamlit_extras.add_vertical_space import add_vertical_space


class linkedin_scraper:

    # =========================================================
    # WebDriver Setup
    # =========================================================
    @staticmethod
    def webdriver_setup():

        options = webdriver.ChromeOptions()

        # Required for Streamlit Cloud / Linux
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")

        # Browser window size
        options.add_argument("--window-size=1920,1080")

        # Prevent unnecessary browser messages
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")

        # Create Chrome/Chromium driver
        driver = webdriver.Chrome(
            options=options
        )

        driver.implicitly_wait(10)

        return driver


    # =========================================================
    # Get User Input
    # =========================================================
    @staticmethod
    def get_userinput():

        add_vertical_space(2)

        with st.form(key="linkedin_scarp"):

            add_vertical_space(1)

            col1, col2, col3 = st.columns(
                [0.5, 0.3, 0.2],
                gap="medium"
            )

            with col1:

                job_title_input = st.text_input(
                    label="Job Title"
                )

                job_title_input = job_title_input.split(",")


            with col2:

                job_location = st.text_input(
                    label="Job Location",
                    value="India"
                )


            with col3:

                job_count = st.number_input(
                    label="Job Count",
                    min_value=1,
                    value=1,
                    step=1
                )


            add_vertical_space(1)

            submit = st.form_submit_button(
                label="Submit"
            )

            add_vertical_space(1)

        return (
            job_title_input,
            job_location,
            job_count,
            submit
        )


    # =========================================================
    # Build LinkedIn Jobs URL
    # =========================================================
    @staticmethod
    def build_url(job_title, job_location):

        keyword = "%20".join(
            job_title[0].split()
        )

        return (
            "https://www.linkedin.com/jobs/search/"
            f"?keywords={keyword}"
            f"&location={job_location}"
        )


    # =========================================================
    # Open LinkedIn
    # =========================================================
    @staticmethod
    def open_link(driver, link):

        driver.get(
            "https://www.linkedin.com/feed/"
        )

        time.sleep(2)

        driver.get(link)

        time.sleep(5)

        driver.refresh()

        time.sleep(3)


    # =========================================================
    # Open Link & Scroll
    # =========================================================
    @staticmethod
    def link_open_scrolldown(
        driver,
        link,
        job_count
    ):

        # Open LinkedIn job search
        linkedin_scraper.open_link(
            driver,
            link
        )

        # Scroll page
        for i in range(0, job_count):

            try:

                body = driver.find_element(
                    by=By.TAG_NAME,
                    value="body"
                )

                body.send_keys(
                    Keys.PAGE_UP
                )

            except Exception:
                pass


            # Scroll to bottom
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )

            time.sleep(2)


            # Click "See more jobs"
            try:

                button = driver.find_element(
                    By.CSS_SELECTOR,
                    "button[aria-label='See more jobs']"
                )

                button.click()

                time.sleep(3)

            except Exception:
                pass


    # =========================================================
    # Job Title Filter
    # =========================================================
    @staticmethod
    def job_title_filter(
        scrap_job_title,
        user_job_title_input
    ):

        # User input → lowercase
        user_input = [
            i.lower().strip()
            for i in user_job_title_input
        ]

        # Scraped title → lowercase
        scrap_title = [
            i.lower().strip()
            for i in [scrap_job_title]
        ]


        confirmation_count = 0

        for i in user_input:

            if all(
                j in scrap_title[0]
                for j in i.split()
            ):

                confirmation_count += 1


        if confirmation_count > 0:

            return scrap_job_title

        else:

            return np.nan


    # =========================================================
    # Scrape Company / Job Data
    # =========================================================
    @staticmethod
    def scrap_company_data(
        driver,
        job_title_input,
        job_location,
        job_count
    ):

        cards = driver.find_elements(
            By.CSS_SELECTOR,
            "li.scaffold-layout__list-item"
        )

        data = []


        for card in cards[:job_count]:

            try:

                # Job Title
                title = card.find_element(
                    By.CSS_SELECTOR,
                    "a.job-card-container__link span[aria-hidden='true']"
                ).text.strip()


                # Company
                company = card.find_element(
                    By.CSS_SELECTOR,
                    "div.artdeco-entity-lockup__subtitle"
                ).text.strip()


                # Location
                location = card.find_element(
                    By.CSS_SELECTOR,
                    "div.artdeco-entity-lockup__caption"
                ).text.strip()


                # Job URL
                url = card.find_element(
                    By.CSS_SELECTOR,
                    "a.job-card-container__link"
                ).get_attribute("href")


                data.append({

                    "Company Name": company,

                    "Job Title": title,

                    "Location": location,

                    "Website URL": url

                })


            except Exception:

                continue


        df = pd.DataFrame(data)


        if len(df) == 0:

            return df


        df.reset_index(
            drop=True,
            inplace=True
        )

        return df


    # =========================================================
    # Scrape Job Description
    # =========================================================
    @staticmethod
    def scrap_job_description(
        driver,
        df,
        job_count
    ):

        # Get URLs
        website_url = df[
            "Website URL"
        ].tolist()


        job_description = []


        for url in website_url[:job_count]:

            try:

                driver.get(url)

                time.sleep(5)


                # Click "Show more" if available
                try:

                    show_more = driver.find_element(
                        By.CSS_SELECTOR,
                        "button.jobs-description__footer-button"
                    )

                    show_more.click()

                    time.sleep(2)

                except Exception:

                    pass


                # Extract description
                description = driver.find_element(
                    By.CSS_SELECTOR,
                    "div.jobs-description__content"
                ).text


                if description.strip():

                    job_description.append(
                        description
                    )

                else:

                    job_description.append(
                        "Description Not available"
                    )


            except Exception:

                job_description.append(
                    "Description not available"
                )


        # Match dataframe rows
        df = df.iloc[
            :len(job_description),
            :
        ].copy()


        df["Job Description"] = job_description


        return df


    # =========================================================
    # Display Data in Streamlit
    # =========================================================
    @staticmethod
    def display_data_userinterface(
        df_final
    ):

        add_vertical_space(1)


        if len(df_final) > 0:

            for i in range(
                0,
                len(df_final)
            ):

                st.markdown(
                    f"""
                    <h3 style="color: orange;">
                    Job Posting Details : {i + 1}
                    </h3>
                    """,
                    unsafe_allow_html=True
                )


                st.write(
                    f"Company Name : "
                    f"{df_final.iloc[i, 0]}"
                )


                st.write(
                    f"Job Title : "
                    f"{df_final.iloc[i, 1]}"
                )


                st.write(
                    f"Location : "
                    f"{df_final.iloc[i, 2]}"
                )


                st.write(
                    f"Website URL : "
                    f"{df_final.iloc[i, 3]}"
                )


                # Job Description
                if "Job Description" in df_final.columns:

                    with st.expander(
                        "Job Description"
                    ):

                        st.write(
                            df_final.iloc[i, 4]
                        )


                add_vertical_space(3)


        else:

            st.markdown(
                """
                <h5 style="text-align: center;color: orange;">
                No Matching Jobs Found
                </h5>
                """,
                unsafe_allow_html=True
            )