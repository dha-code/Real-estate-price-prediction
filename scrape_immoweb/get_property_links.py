import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

start_time = time.perf_counter()

# Function to get cookies for the URL
def get_cookie(url):
    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url) 
    time.sleep(4)

    shadow_host = driver.find_element(By.ID, 'usercentrics-root')
    shadow_root = shadow_host.shadow_root
    elem = shadow_root.find_element(By.CSS_SELECTOR, "button[data-testid='uc-accept-all-button']")
    elem.click()

    cookies = driver.get_cookies()
    driver.quit()
    return cookies

# Function to set cookies for the session
def set_cookie(url,session):
    cookies = get_cookie(url)
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])

all_links = []
exclude_properties = ["new-real-estate-project-apartments","new-real-estate-project-houses","apartment-block","mixed-use-building"]

url = "https://www.immoweb.be/en/search/house-and-apartment/for-sale"
session = requests.Session()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36', #mimics browser
}
set_cookie(url,session)

for page in range(1, 334):
    # Construct the URL for each page
    url = f"https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&isALifeAnnuitySale=false&page={page}&orderBy=relevance"
    response = session.get(url, headers=headers)

    # Reset cookies if expired
    if response.status_code != 200:
        set_cookie(url,session)
        response = session.get(url, headers=headers)

    html = response.content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Loop through all links and exclude properties previously defined
    for a in soup.find_all('a', class_='card__title-link'):
        link = a['href']
        if link:
            if not any(property_type in link for property_type in exclude_properties):
                all_links.append(link)

# Save links to file
with open("ImmoLinks.txt", "w") as file:
    for link in all_links:
        file.write(link + "\n")

print(f"\nTime taken to scrape {time.perf_counter() - start_time} seconds.") 