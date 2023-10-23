import yaml
import json
from bs4 import BeautifulSoup
import requests
import html2text
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
import os
import json
from datetime import datetime
from serpapi import GoogleSearch


config_file = "config.yaml"

# Load the configuration from the YAML file
with open(config_file, 'r') as file:
    config = yaml.safe_load(file)

api_key_serpapi = config['api_keys']['serpapi']

FUNCTIONS=[
    {
        "name": "search",
        "description": "When the user is asking for information you need to google, search for a query and return results",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "web_scrape",
        "description": "Scrape the content from a given URL using BeautifulSoup. Useful if you want to follow up on a search query with more information from a specific website.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to scrape"
                }
            },
            "required": ["url"],
        },
    },
    {
        "name": "vector_search_civil_code",
        "description": "Search for articles based on a query and return top N results. To aid vector search, take the user's question and rewrite it as a hypothetical answer to increase likelihood of vector search match. Write the answer in the style of a sentence that might appear in the Louisiana Civil Code.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Take the user's question and write a one or two sentence hypothetical answer to the question in the style of a sentence that might appear in the Louisiana Civil Code. Use complete sentences. Always use Louisiana terminology, i.e, 'parish' instead of 'county', 'immovable property' instead of 'real estate', etc."
                }
            },
            "required": ["query", "top_n_number"]
        }
    },
    {
        "name": "classify_question",
        "description": "Classify whether you need more information to answer the user's question or not. Useful if you want to know whether to follow up with a search query or not.",
        "parameters": {
            "type": "object",
            "properties": {
                "bool": {
                    "type": "boolean",
                    "description": "True for yes you need more information, False for no you have everything you need."
                }
            },
            "required": ["bool"]
        }
    }
]

def classify_question(bool: bool):
    if bool:
        return "Yes"
    else:
        return "No"

def search(query: str):
    params = {
        "q": query,
        "hl": "en",
        "gl": "us",
        "num": "10",
        "google_domain": "google.com",
        "api_key": f"{api_key_serpapi}"
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    search_results_as_str = ""
    urls = []  # list to collect URLs

    if 'answer_box' in results:
        answer_box = results['answer_box']
        title = answer_box.get('title', 'No title available')
        url = answer_box.get('link', 'No URL available')
        snippet = answer_box.get('snippet', 'No snippet available')
        search_results_as_str += f"\nAnswer Box:\nTitle: {title}\nURL: {url}\nSnippet: {snippet}\n"
        urls.append(url)

    for i, result in enumerate(results['organic_results'], start=1):
        title = result.get('title', 'No title available')
        url = result.get('link', 'No URL available')
        snippet = result.get('snippet', 'No snippet available')
        search_results_as_str += f"\nResult {i}:\nTitle: {title}\nURL: {url}\nSnippet: {snippet}\n"
        urls.append(url)

    response = {
        "snippets": search_results_as_str,
        "query": query,
        "urls": urls
    }

    return json.dumps(response)


def web_scrape(url: str):
    # Define headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # Make the request with headers
    response = requests.get(url, headers=headers)
    
    # Ensure the request was successful
    response.raise_for_status()
    
    # Use html2text to convert HTML to plain text
    text_maker = html2text.HTML2Text()
    text_maker.ignore_links = True   # this can be set to False if you want to include URLs
    plain_text = text_maker.handle(response.text)
    
    return plain_text

