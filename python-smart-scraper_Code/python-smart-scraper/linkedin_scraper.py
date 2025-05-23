"""
LinkedIn Scraper and Data Enrichment Tool
Author: Muzamil
Description: A complex LinkedIn scraping and enrichment tool designed for internal use.
"""

import time
import random
import csv
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

SEARCH_KEYWORDS = "Python Developer San Francisco"
BASE_URL = "https://www.linkedin.com/search/results/people/"
HEADERS = {
    'User-Agent': UserAgent().random,
    'Accept-Language': 'en-US,en;q=0.9',
}

def get_search_url(keyword):
    return f"{BASE_URL}?keywords={keyword.replace(' ', '%20')}&origin=SWITCH_SEARCH_VERTICAL"

def scrape_profiles(search_url, num_pages=2):
    profiles = []
    for page in range(1, num_pages + 1):
        url = f"{search_url}&page={page}"
        print(f"Scraping Page: {page} | URL: {url}")
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print("Request failed. Status code:", response.status_code)
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.find_all('div', {'class': 'entity-result__content'})

        for card in cards:
            name = card.find('span', {'aria-hidden': 'true'})
            title = card.find('div', {'class': 'entity-result__primary-subtitle'})
            location = card.find('div', {'class': 'entity-result__secondary-subtitle'})

            profiles.append({
                'name': name.get_text(strip=True) if name else None,
                'title': title.get_text(strip=True) if title else None,
                'location': location.get_text(strip=True) if location else None,
            })

        time.sleep(random.uniform(2, 4))
    return profiles

def enrich_data(profile):
    profile['skills'] = ['Python', 'APIs', 'Scraping']
    profile['availability'] = 'Available for contract'
    return profile

def save_to_csv(profiles, filename='output/linkedin_contacts.csv'):
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'title', 'location', 'skills', 'availability'])
        writer.writeheader()
        for profile in profiles:
            enriched = enrich_data(profile)
            writer.writerow(enriched)

if __name__ == "__main__":
    search_url = get_search_url(SEARCH_KEYWORDS)
    profiles = scrape_profiles(search_url)
    save_to_csv(profiles)
    print("Scraping complete. Data saved.")
