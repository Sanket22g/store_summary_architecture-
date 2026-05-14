# check_db.py
import chromadb

client     = chromadb.PersistentClient(path="./market_research_db")
collection = client.get_collection("market_research_reports")

# see all stored chunks
results = collection.get(include=["documents", "metadatas"])

print(f"Total chunks stored: {len(results['ids'])}")
print()

for i, (doc, meta) in enumerate(zip(results["documents"], results["metadatas"])):
    print(f"[Chunk {i+1}] Agent: {meta['agent']} | chunk_index: {meta['chunk_index']}")
    print(f"Preview: {doc[:100]}...")
    print("─" * 50)