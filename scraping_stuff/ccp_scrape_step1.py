from bs4 import BeautifulSoup
import csv

# Function to combine relative URL with base URL
def urljoin(base, url):
    from urllib.parse import urljoin  # This module can join relative URLs with base URLs
    return urljoin(base, url)

# Load the HTML content
html_file_path = 'ccphtml.html'  # Replace with the path to your HTML file
with open(html_file_path, 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Specify the base URL
base_url = 'https://www.legis.la.gov/legis/'

# Find all <a> tags within the specific table. Adjust the attributes to find the exact table, if necessary.
a_tags = soup.select('div#ctl00_ctl00_PageBody_PageContent_PanelResults2 table a')

# Prepare data for the CSV file
csv_data = []
for tag in a_tags:
    article_number = tag.get_text(strip=True)  # e.g., "CCP 1"
    relative_url = tag['href']  # e.g., "Law.aspx?d=111103"
    full_url = urljoin(base_url, relative_url)  # Combine to form the full URL

    csv_data.append([article_number, full_url])

# Save data to a CSV file
csv_file_path = 'ccp_articles_urls.csv'  # Name of the output CSV file
with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['CCP Article Number', 'URL'])  # Header row
    writer.writerows(csv_data)

print(f'Data written to {csv_file_path}')
