from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

options = webdriver.EdgeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Edge(
    service=Service(EdgeChromiumDriverManager().install()),
    options=options
)

driver.get("https://www.google.com")

input("Press Enter...")
driver.quit()