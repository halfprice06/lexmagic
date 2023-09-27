# Dependencies
import json  # for parsing the JSON api responses and model outputs
from numpy import dot  # for cosine similarity
import openai  # for using GPT and getting embeddings
import os  # for loading environment variables
import requests  # for making the API requests
import urllib.parse

from datetime import date, timedelta  # for getting the current date

# Load environment variables
court_listener_api_key = "79e0928da97eecf335279f4a03042aa3e4023761"
openai.api_key = "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"


GPT_MODEL = "gpt-4"


# Helper functions
def json_gpt(input: str):
    completion = openai.ChatCompletion.create(
        model=GPT_MODEL,
        messages=[
            {"role": "system", "content": "Output only valid JSON"},
            {"role": "user", "content": input},
        ],
        temperature=0.5,
    )

    text = completion.choices[0].message.content
    parsed = json.loads(text)

    return parsed


def embeddings(input: list[str]) -> list[list[str]]:
    response = openai.Embedding.create(model="text-embedding-ada-002", input=input)
    return [data.embedding for data in response.data]

# User asks a question
USER_QUESTION = urllib.parse.quote(input("Please enter your question: "))

QUERIES_INPUT = f"""
You have access to a search API that returns legal opinions from Louisiana state courts.
Generate an array of search queries that are relevant to this question.
Use a variation of related keywords for the queries, trying to be as general as possible.
Include as many queries as you can think of, including and excluding terms.
For example, include queries like ['keyword_1 keyword_2', 'keyword_1', 'keyword_2'].
Be creative. Include about 5 - 10 queries.

User question: {USER_QUESTION}

Format: {{"queries": ["query_1", "query_2", "query_3"]}}
"""

queries = json_gpt(QUERIES_INPUT)["queries"]

# Let's include the original question as well for good measure
queries.append(USER_QUESTION)

print("Queries: ", queries)


def search_court_listener(
    query: str,
    court_listener_api_key: str = court_listener_api_key,
    num_opinions: int = 10,
) -> dict:
    headers = {
        'Authorization': f'Token {court_listener_api_key}'
    }
    response = requests.get(
        "https://www.courtlistener.com/api/rest/v3/search/",
        headers=headers,
        params={
            "q": query,
            "pageSize": num_opinions,
            "order_by": "score desc",  # changed from "relevancy"
            "type": "o",  # search for opinions
            "stat_Precedential": "on",  # search for precedential cases
            "stat_Non-Precedential": "on",  # search for non-precedential cases
            "court": "la lactapp laag"  # search in specific Louisiana courts
        },
    )

    return response.json()


def get_opinion_text(opinion_id: int, court_listener_api_key: str = court_listener_api_key) -> list[str]:
    headers = {
        'Authorization': f'Token {court_listener_api_key}'
    }
    response = requests.get(
        f"https://www.courtlistener.com/api/rest/v3/opinions/{opinion_id}/",
        headers=headers,
    )
    if response.text:  # Check if the response is not empty
        try:
            opinion = response.json()
        except json.JSONDecodeError:
            print(f"Invalid JSON response for opinion_id: {opinion_id}, status code: {response.status_code}")
            return [""]
        if opinion["html_with_citations"]:
            text = opinion["html_with_citations"]
        elif opinion["xml_harvard"]:
            text = opinion["xml_harvard"]
        elif opinion["plain_text"]:
            text = opinion["plain_text"]
        elif opinion["html"]:
            text = opinion["html"]
        elif opinion["html_lawbox"]:
            text = opinion["html_lawbox"]
        elif opinion["html_columbia"]:
            text = opinion["html_columbia"]
        elif opinion["html_anon_2020"]:
            text = opinion["html_anon_2020"]
        else:
            text = ""
    else:
        print(f"Empty response for opinion_id: {opinion_id}, status code: {response.status_code}")
        return [""]

    # Split the text into chunks of 1000 characters
    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    return chunks


opinions = []

for query in queries:
    result = search_court_listener(query)
    print(result)
    if result["count"] > 0:
        for opinion_preview in result["results"]:
            opinion_text_chunks = get_opinion_text(opinion_preview["id"])
            for chunk in opinion_text_chunks:
                opinions.append({**opinion_preview, "text": chunk})

# remove duplicates
opinions = list({opinion["id"]: opinion for opinion in opinions}.values())

print("Total number of opinions:", len(opinions))
print("Top 5 opinions of query 1:", "\n")

for opinion in opinions[0:5]:
    print("Title:", opinion["caseName"])
    print("Description:", opinion["caseNameShort"])
    print("Content:", opinion["text"][0:100] + "...")
    print()

HA_INPUT = f"""
Generate a hypothetical answer to the user's question. This answer will be used to rank search results. 
Pretend you have all the information you need to answer, but don't use any actual facts. Instead, use placeholders
like NAME did something, or NAME said something at PLACE. 

User question: {USER_QUESTION}

Format: {{"hypotheticalAnswer": "hypothetical answer text"}}
"""

hypothetical_answer = json_gpt(HA_INPUT)["hypotheticalAnswer"]

print("Hypothetical answer: ", hypothetical_answer)

hypothetical_answer_embedding = embeddings(hypothetical_answer)[0]
opinion_embeddings = embeddings(
    [
        f"{opinion['caseName']} {opinion['caseNameShort']} {opinion['text']}"
        for opinion in opinions
    ]
)

# Calculate cosine similarity
cosine_similarities = []
for opinion_embedding in opinion_embeddings:
    cosine_similarities.append(dot(hypothetical_answer_embedding, opinion_embedding))

print("Cosine similarities: ", cosine_similarities[0:10])

scored_opinions = zip(opinions, cosine_similarities)

# Sort opinions by cosine similarity
sorted_opinions = sorted(scored_opinions, key=lambda x: x[1], reverse=True)

# Print top 5 opinions
print("Top 5 opinions:", "\n")

for opinion, score in sorted_opinions[0:5]:
    print("Title:", opinion["caseName"])
    print("Description:", opinion["caseNameShort"])
    print("Content:", opinion["text"][0:100] + "...")
    print("Score:", score)
    print()

formatted_top_results = [
    {
        "title": opinion["caseName"],
        "description": opinion["caseNameShort"],
        "url": opinion["absolute_url"],
        "text": opinion["text"],  # Include the text chunk in the result
    }
    for opinion, _score in sorted_opinions[0:5]
]

ANSWER_INPUT = f"""
Generate an answer to the user's question based on the given search results. 
TOP_RESULTS: {formatted_top_results}
USER_QUESTION: {USER_QUESTION}

Include as much information as possible in the answer. Reference the relevant search result urls as markdown links.
"""

completion = openai.ChatCompletion.create(
    model=GPT_MODEL,
    messages=[
        {
            "role": "user", 
            "content": ANSWER_INPUT + f" TEXT_CHUNKS: {formatted_top_results}"
        }
    ],
    stream=False
)

print("Answer: ", completion.choices[0].message.content)

# Add a counter for the number of opinions that got embedded
embedded_opinions_count = len(opinion_embeddings)
print("Number of opinions that got embedded: ", embedded_opinions_count)






