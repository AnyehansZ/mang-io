"""
search_email.py
----------------
1. Fetches your 20 most recent emails from Gmail.
2. Converts each email body into a meaning-vector (embedding).
3. Stores vectors + metadata in ChromaDB (local, no server).
4. Lets you search by meaning — not just keywords.
"""

from sentence_transformers import SentenceTransformer
import chromadb
from utils.gmail import get_gmail_service, fetch_emails


def build_search_index(emails):
    print("Loading embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Model ready.\n")

    client = chromadb.Client()
    collection = client.create_collection(name="inbox")

    ids = [email['id'] for email in emails]
    texts = [email['body'] for email in emails]
    metadatas = [
        {'subject': str(e['subject']), 'sender': str(e['sender']), 'date': str(e['date'])}
        for e in emails
    ]

    print(f"Embedding {len(emails)} emails...")
    embeddings = model.encode(texts).tolist()

    collection.add(embeddings=embeddings, documents=texts, metadatas=metadatas, ids=ids)
    print("Index built.\n")
    return model, collection


def search(query, model, collection, top_k=5):
    query_embedding = model.encode([query]).tolist()
    return collection.query(query_embeddings=query_embedding, n_results=top_k)


def display_results(results):
    if not results['ids'][0]:
        print("No matching emails found.\n")
        return

    print(f"\nFound {len(results['ids'][0])} matching emails:\n")
    print("=" * 70)
    for i in range(len(results['ids'][0])):
        metadata = results['metadatas'][0][i]
        body = results['documents'][0][i]
        distance = results['distances'][0][i] if 'distances' in results else None
        relevance = max(0, int((1 - distance / 2) * 100)) if distance is not None else "?"

        print(f"📧 Result {i+1}  (Relevance: {relevance}%)")
        print(f"   Subject: {metadata['subject']}")
        print(f"   From:    {metadata['sender']}")
        print(f"   Date:    {metadata['date']}")
        print(f"   Preview: {body[:200]}...")
        print("-" * 70)


def main():
    print("\n" + "=" * 70)
    print("  EMAIL SEMANTIC SEARCH")
    print("=" * 70 + "\n")

    service = get_gmail_service()
    emails = fetch_emails(service, max_results=20, min_body_length=50, show_progress=True)
    if not emails:
        print("No emails found.")
        return

    model, collection = build_search_index(emails)

    print("You can now search your inbox by meaning, not just keywords.\n")
    print("Examples:")
    print('  "shipping confirmation"')
    print('  "meeting about budget"')
    print('  "newsletter with tech news"')
    print('  "receipt from online store"\n')
    print("Type 'exit' to quit.\n")

    while True:
        query = input("🔍 Search: ").strip()
        if query.lower() == 'exit':
            print("Goodbye.")
            break
        if not query:
            continue
        results = search(query, model, collection, top_k=5)
        display_results(results)


if __name__ == '__main__':
    main()