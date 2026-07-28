import time
import numpy as np
import pandas as pd
import streamlit as st

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from streamlit_extras.add_vertical_space import add_vertical_space
from selenium.webdriver.edge.service import Service


from webdriver_manager.microsoft import EdgeChromiumDriverManager

from selenium.common.exceptions import NoSuchElementException
class linkedin_scraper:
   
    @staticmethod
    def webdriver_setup():
        options = webdriver.EdgeOptions()
        options.add_argument('--start-maximized')
        
        options.add_argument(
            r"--user-data-dir=C:\EdgeSeleniumProfile"
        )
    
        
        #Existing chrome profile
        driver = webdriver.Edge(
            service=Service(EdgeChromiumDriverManager().install()),
            options=options
        )
        driver.implicitly_wait(10)
        return driver

    @staticmethod
    def get_userinput():

        add_vertical_space(2)
        with st.form(key='linkedin_scarp'):

            add_vertical_space(1)
            col1,col2,col3 = st.columns([0.5,0.3,0.2], gap='medium')
            with col1:
                job_title_input = st.text_input(label='Job Title')
                job_title_input = job_title_input.split(',')
            with col2:
                job_location = st.text_input(label='Job Location', value='India')
            with col3:
                job_count = st.number_input(label='Job Count', min_value=1, value=1, step=1)

            # Submit Button
            add_vertical_space(1)
            submit = st.form_submit_button(label='Submit')
            add_vertical_space(1)
        
        return job_title_input, job_location, job_count, submit

    @staticmethod
    def build_url(job_title, job_location):
        keyword = "%20".join(job_title[0].split())

        
        

        return (
            f"https://www.linkedin.com/jobs/search/"
            f"?keywords={keyword}"
            f"&location={job_location}"
        )
    
    @staticmethod
    def open_link(driver, link):
        driver.get("https://www.linkedin.com/feed/")
        time.sleep(2)

        driver.get(link)
        time.sleep(5)

        driver.refresh()
        time.sleep(3)

    @staticmethod
    def link_open_scrolldown(driver, link, job_count):
        
        # Open the Link in LinkedIn
        linkedin_scraper.open_link(driver, link)

        # Scroll Down the Page
        for i in range(0,job_count):

            # Simulate clicking the Page Up button
            body = driver.find_element(by=By.TAG_NAME, value='body')
            body.send_keys(Keys.PAGE_UP)

            # Locate the sign-in modal dialog 
            

            # Scoll down the Page to End
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            driver.implicitly_wait(2)

            # Click on See More Jobs Button if Present
            try:
                x = driver.find_element(by=By.CSS_SELECTOR, value="button[aria-label='See more jobs']").click()
                driver.implicitly_wait(5)
            except:
                pass

    @staticmethod
    def job_title_filter(scrap_job_title, user_job_title_input):
        
        # User Job Title Convert into Lower Case
        user_input = [i.lower().strip() for i in user_job_title_input]

        # scraped Job Title Convert into Lower Case
        scrap_title = [i.lower().strip() for i in [scrap_job_title]]

        # Verify Any User Job Title in the scraped Job Title
        confirmation_count = 0
        for i in user_input:
            if all(j in scrap_title[0] for j in i.split()):
                confirmation_count += 1

        # Return Job Title if confirmation_count greater than 0 else return NaN
        if confirmation_count > 0:
            return scrap_job_title
        else:
            return np.nan

    @staticmethod
    def scrap_company_data(driver, job_title_input, job_location,job_count):
        cards=driver.find_elements(
            By.CSS_SELECTOR,
            "li.scaffold-layout__list-item"
        )
        data=[]

        for card in cards[:job_count]:
            try:

                title=card.find_element(
                    By.CSS_SELECTOR,
                    "a.job-card-container__link span[aria-hidden='true']"
                ).text.strip()

                company=card.find_element(
                    By.CSS_SELECTOR,
                    "div.artdeco-entity-lockup__subtitle"
                ).text.strip()

                location=card.find_element(
                    By.CSS_SELECTOR,
                    "div.artdeco-entity-lockup__caption"
                ).text.strip()

                url=card.find_element(
                    By.CSS_SELECTOR,
                    "a.job-card-container__link"
                ).get_attribute("href")

                data.append({
                    "Company Name":company,
                    "Job Title":title,
                    "Location":location,
                    "Website URL":url
                })

            except Exception:
                continue
        df = pd.DataFrame(data)

        if len(df)==0:
            return df

        # df["Job Title"] = df["Job Title"].apply(
        #     lambda x: linkedin_scraper.job_title_filter(x,job_title_input)
        # )

        # df["Location"]=df["Location"].apply(
        #     lambda x: x if job_location.lower() in x.lower() else np.nan
        # )

        # df.dropna(inplace=True)
        print(df)
        df.reset_index(drop=True, inplace=True)
        return df
        
    @staticmethod
    def scrap_job_description(driver, df, job_count):
        
        # Get URL into List
        website_url = df['Website URL'].tolist()
        
        # Scrap the Job Description
        job_description = []
        description_count = 0

        for url in website_url[:job_count]:
            try:
                driver.get(url)
                time.sleep(5)
                print("=" * 80)
                print("Current URL :", driver.current_url)
                print("Page Title  :", driver.title)
                # Screenshot save karega
                driver.save_screenshot("job_page.png")
                try:
                    show_more=driver.find_element(
                        By.CSS_SELECTOR,
                        "button.jobs-description__footer-button"
                    )
                    show_more.click()
                    time.sleep(2)
                except:
                    pass

                description=driver.find_element(
                    By.CSS_SELECTOR,
                    "div.jobs-description__content"
                ).text
                if description.strip():
                    job_description.append(description)
                else:
                    job_description.append("Description Not available")
            except Exception:
                job_description.append("Description not available")
        df = df.iloc[:len(job_description),:]
        df["Job Description"]=job_description
        return df
               
    @staticmethod
    def display_data_userinterface(df_final):

        # Display the Data in User Interface
        add_vertical_space(1)
        if len(df_final) > 0:
            for i in range(0, len(df_final)):
                
                st.markdown(f'<h3 style="color: orange;">Job Posting Details : {i+1}</h3>', unsafe_allow_html=True)
                st.write(f"Company Name : {df_final.iloc[i,0]}")
                st.write(f"Job Title    : {df_final.iloc[i,1]}")
                st.write(f"Location     : {df_final.iloc[i,2]}")
                st.write(f"Website URL  : {df_final.iloc[i,3]}")

                # with st.expander(label='Job Desription'):
                #     st.write(df_final.iloc[i, 4])
                add_vertical_space(3)
        
        else:
            st.markdown(f'<h5 style="text-align: center;color: orange;">No Matching Jobs Found</h5>', 
                                unsafe_allow_html=True)

# if __name__ == "__main__":

#     driver = linkedin_scraper.webdriver_setup()

#     driver.get("https://www.linkedin.com/jobs/search/?keywords=Data%20Analyst&location=India")

#     time.sleep(8)

#     df = linkedin_scraper.scrap_company_data(
#         driver,
#         ["Data Analyst"],
#         "India"
#     )

#     print(df)

#     print("\nFetching Job Descriptions...\n")

#     df = linkedin_scraper.scrap_job_description(
#         driver,
#         df,
#         3          # sirf first 3 jobs test ke liye
#     )

#     print(df[["Company Name", "Job Description"]])

#     input("Press Enter...")

#     driver.quit()