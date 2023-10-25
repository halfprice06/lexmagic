def vector_search_civil_code(query, top_n_number=10):
    import chromadb
    import sqlite3
    import logging

    logging.basicConfig(level=logging.ERROR)

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

    # Initialize Chroma Client and load existing database
    chroma_client = chromadb.PersistentClient("vdb")

    # Get the existing collection
    collection = chroma_client.get_collection(name="civil_code_articles")

    # Query Chroma DB
    results = collection.query(query_texts=[query], n_results=top_n_number)

    # Extract individual lists
    ids_list = results.get('ids', [])[0]  # Extracting the first list from the 'ids'
    documents_list = results.get('documents', [])[0]  # Extracting the first list from the 'documents'
    metadatas_list = results.get('metadatas', [])[0]  # Extracting the first list from the 'metadatas'
    distances_list = results.get('distances', [])[0]  # Extracting the first list from the 'distances'

    # Prepare the output string
    output = ""
    top_articles = []

    # Loop through the extracted lists
    for idx, doc, meta, dist in zip(ids_list, documents_list, metadatas_list, distances_list):

        # Add the current article to the output
        output += f"La. Civil Code Article {idx} - {meta.get('article_title')}\n"
        output += f"Content: {doc}\n"
        output +=  "\n\n"
        top_articles.append(f"La. Civil Code Article {idx} - {meta.get('article_title')}\n{doc}")

        # Insert the result into the SQLite database
        c.execute('''
            INSERT INTO results (id, content, source, distance, query)
            VALUES (?, ?, ?, ?, ?)
        ''', (idx, doc, meta.get('article_title'), dist, query))
    conn.commit()

    return output, top_articles


def repl():
    while True:
        query = input("Enter your query (or 'quit' to exit): ")
        if query.lower() == 'quit':
            break
        top_n_number = int(input("Enter the number of top results you want: "))
        result = vector_search_civil_code(query, top_n_number)
        print(result)

if __name__ == "__main__":
    repl()