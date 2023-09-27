def vector_search_civil_code(query, top_n_number=10):
    import csv
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

    # Function to read the CSV and prepare documents, metadatas, and ids
    def read_csv_data(filepath):
        documents = []
        metadatas = []
        ids = []

        with open(filepath, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                documents.append(row['article_content'])
                metadatas.append({"article_title": row['article_title']})
                ids.append(row['article_number'])

        return documents, metadatas, ids

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

    # Loop through the extracted lists
    for idx, doc, meta, dist in zip(ids_list, documents_list, metadatas_list, distances_list):

        # Get the index of the current article in the ids list
        current_index = ids_list.index(idx)

        # Get the articles before and after the current article
        before_articles = ids_list[max(0, current_index - 2):current_index]
        after_articles = ids_list[current_index + 1:min(len(ids_list), current_index + 3)]

        # Add the before articles to the output only for the top result
        if idx == ids_list[0]:
            for before_article in before_articles:
                output += f"Article Number: {before_article}\n"
                output += f"Article Title: {metadatas_list[ids_list.index(before_article)].get('article_title')}\n"
                output += f"Content: {documents_list[ids_list.index(before_article)]}\n"
                output += "-" * 50 + "\n"

        # Add the current article to the output
        output += f"Article Number: {idx}\n"
        output += f"Article Title: {meta.get('article_title')}\n"
        output += f"Content: {doc}\n"
        output += "-" * 50 + "\n"

        # Add the after articles to the output only for the top result
        if idx == ids_list[0]:
            for after_article in after_articles:
                output += f"Article Number: {after_article}\n"
                output += f"Article Title: {metadatas_list[ids_list.index(after_article)].get('article_title')}\n"
                output += f"Content: {documents_list[ids_list.index(after_article)]}\n"
                output += "-" * 50 + "\n"

        # Insert the result into the SQLite database
        c.execute('''
            INSERT INTO results (id, content, source, distance, query)
            VALUES (?, ?, ?, ?, ?)
        ''', (idx, doc, meta.get('article_title'), dist, query))
    conn.commit()

    return output


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