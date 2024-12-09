import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time 
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from utils.PropertyDataScraper import PropertyDataScraper

start_time = time.perf_counter()

# Function to obtain the cookies after clicking consent box using Selenium
def get_cookie(url):
    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url) 
    time.sleep(5)

    shadow_host = driver.find_element(By.ID, 'usercentrics-root')
    shadow_root = shadow_host.shadow_root
    elem = shadow_root.find_element(By.CSS_SELECTOR, "button[data-testid='uc-accept-all-button']")
    elem.click()

    cookies = driver.get_cookies()
    driver.quit()
    return cookies

# Function to set the cookies in the requests-session object
def set_cookie(url,session):
    cookies = get_cookie(url)
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])

# Writing to output file - locked so that only one thread can write at a time
def write_to_file(lock, file_path, data):
    with lock:
        with open(file_path, "a") as file:
            file.write(data + "\n")

# Function to scrape the HTML page and send it to PropertyDataScraper for data extraction
def scrape_url(session, url, headers, file_path, lock):
    try:
        response = session.get(url, headers=headers, timeout=8)
        response.raise_for_status()
        # Try resetting cookies if that is the issue
        if response.status_code != 200:
            set_cookie(url,session)
            response = session.get(url, headers=headers)

        # Proceed only if the link can be accessed 
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            property_data = PropertyDataScraper(soup,url)
            scraped_data = property_data.return_data()
            write_to_file(lock, file_path, f"{scraped_data}")  # Write URL and data
    except:
        # Print to console if some link is inaccessible
        print("Skipping ",url,response.status_code)

# Function to multithread the scraping process  
def scrape_all_links(session, urls, headers, output_file, max_threads):
    lock = Lock() # Required for file writing 
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        # Submitting each URL to the thread pool
        for url in urls:
            executor.submit(scrape_url, session, url, headers, output_file, lock)

if __name__ == "__main__":
    # First obtain the cookies for the URLand set it in the sessions object
    url = "https://www.immoweb.be/en/search/house-and-apartment/for-sale"
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36', #mimics browser
    }
    set_cookie(url,session)

    # Read all the immo links stored in the input file
    with open("ImmoLinks.txt", "r") as file:
        property_urls = [line.strip() for line in file]

    # Create file and write the first row 
    first_row = "Property type,Locality,Subtype,Construction year,Price,Type sale,Bedrooms,Living area,Equipped kitchen,Furnished,Bathrooms,Open fire,EPC score,Terrace,Terrace Area,Garden,Garden Area,Land surface,Facades,Swimming pool,Building state,URL"
    output_file = "PropertyData.csv"
    
    with open(output_file, "w") as out_handle:
        out_handle.write(first_row + "\n")
        
    # Start scraping all the links 
    scrape_all_links(session, property_urls, headers, output_file, max_threads=4)

# Time check!
print(f"\nTime taken to scrape {time.perf_counter() - start_time} seconds.") 