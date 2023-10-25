# Import required libraries
import sqlite3
import chromadb

# Function to read the SQLite DB and prepare documents, metadatas, and ids
def read_db_data(db_name, table_name):
    documents = []
    metadatas = []
    ids = []

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")

    for row in cursor.fetchall():
        # Concatenate article number, title and content
        document = f"{row[0]} {row[2]} {row[3]}"
        documents.append(document)
        title = row[2] if row[2] is not None else "No title"
        metadatas.append({"article_title": title, "url": row[1]})
        ids.append(row[0])

    return documents, metadatas, ids

# Initialize Chroma Client and load existing database
chroma_client = chromadb.PersistentClient("la_laws_db")

# Create collections
cc_articles_collection = chroma_client.create_collection(name="cc_articles")
ccp_articles_collection = chroma_client.create_collection(name="ccp_articles")
ccrp_articles_collection = chroma_client.create_collection(name="ccrp_articles")

# Add data to Chroma DB from the SQLite DB
db_name = "la_laws.db"
tables = ["cc_articles", "ccp_articles", "ccrp_articles"]
collections = [cc_articles_collection, ccp_articles_collection, ccrp_articles_collection]

for table, collection in zip(tables, collections):
    documents, metadatas, ids = read_db_data(db_name, table)
    collection.add(documents=documents, metadatas=metadatas, ids=ids)

print('Done!')


