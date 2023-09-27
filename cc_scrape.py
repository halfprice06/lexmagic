import requests
from bs4 import BeautifulSoup
import os
import csv
import time

# Create a directory to store the articles if it doesn't exist
if not os.path.exists('Civil_Code_Articles'):
    os.makedirs('Civil_Code_Articles')

# Read the article URLs from the CSV file
article_urls = []
with open('civil_code_articles_complete_url.csv', 'r', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # Skip the header
    for row in reader:
        article_urls.append(row[1])

# Loop through each URL to scrape the article content
for index, url in enumerate(article_urls):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the div containing the article content
        article_div = soup.find('div', {'id': 'ctl00_PageBody_divLaw'})
        
        # Extract the article number and content
        article_number = article_div.find('span', {'id': 'ctl00_PageBody_LabelName'}).text.strip()
        article_content = article_div.find('span', {'id': 'ctl00_PageBody_LabelDocument'}).text.strip()
        
        # Save the article content to a .txt file
        with open(f'Civil_Code_Articles/{article_number}.txt', 'w', encoding='utf-8') as f:
            f.write(article_content)
            
        print(f"Saved {article_number}.txt")
        
        # Rate limiting: sleep for 5 seconds every 500 articles
        if (index + 1) % 500 == 0:
            time.sleep(5)
    else:
        print(f"Failed to fetch {url}")
