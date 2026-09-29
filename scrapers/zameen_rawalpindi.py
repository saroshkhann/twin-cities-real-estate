import pandas as pd 
import numpy as np 
import requests 
import time
import random
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

base_url = "https://www.zameen.com/Plots/Rawalpindi-41-{}.html"

all_plots = []

START_PAGE = 1
MAX_PAGE = 130

for page in range(START_PAGE, MAX_PAGE +1):
    url = base_url.format(page)

    print(f"Scraping page {page}...")
    print(f"[{page}/{MAX_PAGE}] Fetching: {url}")


    try:
        respone = requests.get(url, headers=headers, timeout=15)

        if respone.status_code == 403:
            print(f"Encountered forbidden on page {page}. Sleeping 60s before try again")
            time.sleep(60)
            respone = requests.get(url, headers=headers, timeout=15)

            if respone.status_code != 200:
                print(f"Persistent failure on page {page} ({respone.status_code}). Stopping")
                break
        elif respone.status_code != 200:
            print(f"Unexpected status code {respone.status_code} on page {page}. Stopping")
            break
        
        soup = BeautifulSoup(respone.text, 'lxml')

        cards = soup.find_all('li', role='article')

        if not cards:
            cards = soup.find_all('article')

        for card in cards:
            price_tag = card.find('span', {'aria-label': 'Price'})
            price = price_tag.get_text(strip=True) if price_tag else None

            loc_tag = card.find('div', {'aria-label': 'Location'})
            location = loc_tag.get_text(strip=True) if loc_tag else None

            area_tag = card.find('span', {'aria-label': 'Area'})
            area =area_tag.get_text(strip=True) if area_tag else None

            title_tag = card.find('h2') or card.find('a', title=True)
            title = title_tag.get_text(strip=True) if title_tag else None

            link_tag = card.find('a', href=True)
            link = ("https://www.zameen.com" + link_tag['href']) if link_tag else None
            
            if price or location:
                all_plots.append({
                    'title':title,
                    'price': price,
                    'location': location,
                    'area': area,
                    'link': link,
                    'page_scraped': page
                })
        if page % 50 == 0:
            checkpoint_df = pd.DataFrame(all_plots)
            checkpoint_df.to_csv('data/raw/rawalpindi_checkpoint.csv', index=False)
            print(f"Check point saved: {len(checkpoint_df)} records found ")
        
        time.sleep(random.uniform(2.0,4.0))
    

    except requests.exceptions.RequestException as e:
        print(f"Network error on page {page}: {e}. Halting run.")
    
    except Exception as e:
        print(f"Unexpected error on page {page}: {e}. Halting run.")

df = pd.DataFrame(all_plots)

if not df.empty:
    df.to_csv('data/raw/rawalpindi_raw.csv', index=False)
    print(f"Scraping complete! Total plot saved: {len(df)}")
else:
    print("\nNo data was collected")


