# Import required libraries
import csv
import chromadb
import sqlite3

# Create a new SQLite database and table if they don't exist
conn = sqlite3.connect('results.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER,
        content TEXT,
        source TEXT,
        distance REAL,
        query TEXT
    )
''')
conn.commit()


# Function to read the CSV and prepare documents, metadatas, and ids
def read_csv_data(filepath):
    documents = []
    metadatas = []
    ids = []

    with open(filepath, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Concatenate article number, title and content
            document = f"{row['article_number']} {row['article_title']} {row['article_content']}"
            documents.append(document)
            metadatas.append({"article_title": row['article_title']})
            ids.append(row['article_number'])

    return documents, metadatas, ids

# Initialize Chroma Client and load existing database
chroma_client = chromadb.PersistentClient("vdb")

# Get the existing collection
collection = chroma_client.create_collection(name="civil_code_articles")

# Add data to Chroma DB from the CSV
filepath = "articles.csv"
documents, metadatas, ids = read_csv_data(filepath)
collection.add(documents=documents, metadatas=metadatas, ids=ids)

print('Done!')

