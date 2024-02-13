from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

import time

# Article class
class Article:

    # Init function
    def __init__(self, id, title, authors, date):
        self.id = id
        self.title = title
        self.authors = authors
        self.date = date

def scrape_arxiv_articles(driver_path=r'C:\chromedriver-win64\chromedriver.exe'):
    try:
        # Create a Service object with the path to ChromeDriver
        service = Service(executable_path=driver_path)

        # Initialize the WebDriver for Chrome using the Service object
        driver = webdriver.Chrome(service=service)

        # Open Google Scholar
        driver.get('https://arxiv.org/search/cs?query=%22Artificial+Intelligence%22+OR+%22Machine+Learning%22+OR+%22Deep+Learning%22&searchtype=all&abstracts=show&order=-announced_date_first&size=50')

        # Array to store each article 
        articles = []

        for x in range(1, 50):

            for i in range(1, 51):  # Iterate 50 times, as there are 50 articles per page

                # Extract ID from article
                ID_selector = f'#main-container > div.content > ol > li:nth-child({i}) > div > p > a'
                ID_element = driver.find_element(By.CSS_SELECTOR, ID_selector)
                ID = ID_element.text

                # Extract title from article
                title_selector = f'#main-container > div.content > ol > li:nth-child({i}) > p.title.is-5.mathjax'
                title_element = driver.find_element(By.CSS_SELECTOR, title_selector)
                title = title_element.text

                # Extract authors from article
                authors_selector = f'#main-container > div.content > ol > li:nth-child({i}) > p.authors'
                authors_element = driver.find_element(By.CSS_SELECTOR, authors_selector)
                authors = authors_element.text

                # Extract date from article 
                date_selector = f'#main-container > div.content > ol > li:nth-child({i}) > p:nth-child(5)'
                date_element = driver.find_element(By.CSS_SELECTOR, date_selector)
                date = date_element.text

                # Append the article to the articles list
                articles.append(Article(id = ID, title = title, authors = authors, date = date))

                # Print the article details
                for arts in articles:
                    print(arts.id)
                    print(arts.title)

            # Attempt to find and click the 'Next' button
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#main-container > div.content > nav:nth-child(5) > a.pagination-next"))
                )
                next_button.click()

                # Wait for the next page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#main-container > div.content > ol > li:nth-child(1) > p.title.is-5.mathjax"))
                )
            except Exception:
                # Break the loop if 'Next' button not found or at the end of pages
                print("No next!")
                break

            # Wait a bit before scraping next page
            time.sleep(5)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Ensure the browser is closed
        if driver:
            driver.quit()

        return articles

