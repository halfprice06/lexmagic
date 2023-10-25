from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin  # This module can join relative URLs with base URLs

# Function to combine relative URL with base URL
def urljoin_wrapper(base, url):
    return urljoin(base, url)

# Load the HTML content
html_file_path = 'civil_code.html'  # Replace with the path to your HTML file
with open(html_file_path, 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Specify the base URL
base_url = 'https://www.legis.la.gov/legis/'

# Find all <tr> tags within the specific table. Adjust the attributes to find the exact table, if necessary.
rows = soup.select('div#ctl00_ctl00_PageBody_PageContent_PanelResults2 table tr')

# Prepare data for the CSV file
csv_data = []
for row in rows:
    cells = row.find_all('td')  # Get all td elements in the row

    # Check if the row contains the necessary cells
    if len(cells) == 2:
        # Cell 0 contains the article number
        article_number = cells[0].get_text(strip=True)
        relative_url = cells[0].find('a')['href']
        full_url = urljoin_wrapper(base_url, relative_url)

        # Cell 1 contains the article title
        article_title = cells[1].get_text(strip=True)

        csv_data.append([article_number, full_url, article_title])

# Save data to a CSV file
csv_file_path = 'cc_article_urls.csv'  # Name of the output CSV file
with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['CC Article Number', 'URL', 'Article Title'])  # Header row
    writer.writerows(csv_data)

print(f'Data written to {csv_file_path}')
