import chromadb
import logging

def vector_search_civil_code(query, collections=['cc_articles', 'ccp_articles', 'ccrp_articles'], top_n_number=10):

    logging.basicConfig(level=logging.ERROR)

    # Initialize Chroma Client and load existing database
    chroma_client = chromadb.PersistentClient("la_laws_db")

    # Prepare the output string
    output = ""
    all_articles = []

    # Loop through the collections
    for collection_name in collections:
        # Get the existing collection
        collection = chroma_client.get_collection(name=collection_name)

        # Query Chroma DB
        results = collection.query(query_texts=[query], n_results=top_n_number)

        # Extract individual lists
        ids_list = results.get('ids', [])[0]  # Extracting the first list from the 'ids'
        documents_list = results.get('documents', [])[0]  # Extracting the first list from the 'documents'
        metadatas_list = results.get('metadatas', [])[0]  # Extracting the first list from the 'metadatas'
        distances_list = results.get('distances', [])[0]  # Extracting the first list from the 'distances'

        # Loop through the extracted lists
        for idx, doc, meta, dist in zip(ids_list, documents_list, metadatas_list, distances_list):
            # Add the current article to the all_articles list
            all_articles.append((dist, doc))

    # Sort all_articles by distance and take the top_n_number of articles
    all_articles.sort()
    top_articles = all_articles[:top_n_number]

    # Prepare the output string with top_articles
    for dist, article in top_articles:
        output += f"{article}\n\n"

    return output, [article for _, article in top_articles]

