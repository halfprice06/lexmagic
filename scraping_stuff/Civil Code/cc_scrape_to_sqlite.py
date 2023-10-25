import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import time

# Load the data
file_path = 'cc_article_urls.csv'  # Update this path
data = pd.read_csv(file_path)

# Connect to SQLite database
conn = sqlite3.connect('la_laws.db')
c = conn.cursor()

# Check if table already exists, if not, create it
c.execute('''
    CREATE TABLE IF NOT EXISTS cc_articles (
        article_number TEXT,
        url TEXT,
        title TEXT,
        content TEXT
    )
''')

# Function to scrape content
def scrape_content(url):
    try:
        # Send a request to the URL
        response = requests.get(url)

        # If request was successful
        if response.status_code == 200:
            # Parse HTML content
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the target section
            content_section = soup.find('span', {'id': 'ctl00_PageBody_LabelDocument'})

            # Convert <br> to newlines before getting text
            for br in content_section.find_all("br"):
                br.replace_with("\n")

            # Convert paragraph endings to newlines before getting text
            for p in content_section.find_all("p"):
                p.append("\n\n")  # Add two newlines; one for the line break and one to separate the paragraphs

            # Get text, but keep the line breaks
            content = content_section.get_text(separator="\n", strip=True)

            return content
        else:
            print(f"Failed to retrieve page: {url} (Status code: {response.status_code})")
            return None
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None


# Iterate over each row of the DataFrame, adding a delay every 500 articles
for index, row in data.iterrows():
    print(f"Processing record {index+1}/{len(data)}: {row['URL']}")

    # Scrape the content
    article_content = scrape_content(row['URL'])

    # If we have content, insert it into the SQLite database
    if article_content:
        c.execute('''
            INSERT INTO cc_articles (article_number,url,title,content)
            VALUES (?, ?, ?, ?)
        ''', (row['cc_article_number'], row['URL'], row['article_title'], article_content))

    # After every 500 articles, pause for 5 seconds
    if (index + 1) % 500 == 0:
        print("Processed 500 articles. Pausing for 5 seconds...")
        time.sleep(5)

conn.commit()
conn.close()
