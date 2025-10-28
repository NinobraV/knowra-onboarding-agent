# Embeddings

Local cache for embeddings before pushing to Pinecone

There are two steps to call the embeddings:
1. Create embeddings for the documents
2. Create embeddings for the queries

function create_embeddings create embeddings for the queries because it is used to search for the most similar documents to the query.

the other embeddings is from chromadb
