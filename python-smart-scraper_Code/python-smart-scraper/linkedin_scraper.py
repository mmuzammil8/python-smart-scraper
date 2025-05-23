"""
LinkedIn Scraper and Data Enrichment Tool
Author: Muzamil
Description: A complex LinkedIn scraping and enrichment tool designed for internal use.
"""

import time
import random
import csv
import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# Configuration
SEARCH_KEYWORDS = "Python Developer San Francisco"
BASE_URL = "https://www.linkedin.com/search/results/people/"
USER_AGENT = UserAgent()
HEADERS = {
    'User-Agent': USER_AGENT.random,
    'Accept-Language': 'en-US,en;q=0.9',
}
PROXIES = [
    {'http': 'http://proxy1.example.com:8080'},
    {'http': 'http://proxy2.example.com:8080'},
    None  # fallback to direct connection
]

def get_search_url(keyword):
    return f"{BASE_URL}?keywords={keyword.replace(' ', '%20')}&origin=SWITCH_SEARCH_VERTICAL"

def make_request(url, retries=3):
    for attempt in range(retries):
        try:
            headers = HEADERS.copy()
            headers['User-Agent'] = USER_AGENT.random
            proxy = random.choice(PROXIES)
            logging.info(f"Attempting request with proxy: {proxy}")
            response = requests.get(url, headers=headers, proxies=proxy, timeout=10)
            if response.status_code == 200:
                return response
            logging.warning(f"Non-200 status: {response.status_code}")
        except Exception as e:
            logging.error(f"Request failed: {e}")
        time.sleep(2 ** attempt)  # exponential backoff
    return None

def parse_profile_card(card):
    try:
        name = card.find('span', {'aria-hidden': 'true'})
        title = card.find('div', {'class': 'entity-result__primary-subtitle'})
        location = card.find('div', {'class': 'entity-result__secondary-subtitle'})
        if name and title and location:
            return {
                'name': name.get_text(strip=True),
                'title': title.get_text(strip=True),
                'location': location.get_text(strip=True)
            }
    except Exception as e:
        logging.warning(f"Failed to parse card: {e}")
    return None

def scrape_profiles(search_url, num_pages=2):
    profiles = []
    for page in range(1, num_pages + 1):
        url = f"{search_url}&page={page}"
        logging.info(f"Scraping Page: {page} | URL: {url}")
        response = make_request(url)
        if not response:
            logging.warning("Skipping page due to failed request.")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.find_all('div', {'class': 'entity-result__content'})

        for card in cards:
            profile = parse_profile_card(card)
            if profile:
                profiles.append(profile)

        time.sleep(random.uniform(1, 3))  # polite delay
    return profiles

def enrich_data(profile):
    profile['skills'] = ['Python', 'APIs', 'Scraping']
    profile['availability'] = random.choice(['Available', 'Not Available'])
    profile['ml_score'] = round(random.uniform(0.6, 0.95), 2)  # pseudo scoring
    return profile

def save_to_csv(profiles, filename='output/linkedin_contacts.csv'):
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        fieldnames = ['name', 'title', 'location', 'skills', 'availability', 'ml_score']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for profile in profiles:
            enriched = enrich_data(profile)
            writer.writerow(enriched)

if __name__ == "__main__":
    search_url = get_search_url(SEARCH_KEYWORDS)
    profiles = scrape_profiles(search_url)
    if profiles:
        save_to_csv(profiles)
        logging.info("Scraping complete. Data saved.")
    else:
        logging.warning("No profiles scraped.")
