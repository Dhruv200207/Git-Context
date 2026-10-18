
import uuid

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION_NAME = "gitcontext_chunks"

embedding_model = SentenceTransformer(MODEL_NAME)
VECTOR_SIZE = embedding_model.get_embedding_dimension()

# Local persistent vector database
client = QdrantClient(path=".qdrant")


def create_collection():
    """Create the vector collection if it does not exist."""

    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=VECTOR_SIZE,
                distance=models.Distance.COSINE,
            ),
        )


def reset_collection():
    """
    Recreate the collection to remove stale records.

    WARNING: This deletes all indexed repositories in this collection.
    Use this when you want a fresh, single-repository index.
    """

    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)

    create_collection()
    print("Vector collection reset successfully.")


def index_chunks(chunks):
    """Embed code chunks and save their metadata to Qdrant."""

    if not chunks:
        print("No chunks to index.")
        return

    create_collection()

    texts = [chunk["code"] for chunk in chunks]

    vectors = embedding_model.encode(
        texts,
        normalize_embeddings=True,
    ).tolist()

    points = []

    for chunk, vector in zip(chunks, vectors):
        owner = chunk.get("repo_owner", "")
        repo = chunk.get("repo_name", "")
        branch = chunk.get("branch", "")

        unique_key = (
            f"{owner}/{repo}/{branch}/"
            f"{chunk['file_path']}:{chunk['start_line']}"
        )

        point_id = str(
            uuid.uuid5(uuid.NAMESPACE_URL, unique_key)
        )

        payload = {
            "file_path": chunk["file_path"],
            "chunk_name": chunk["chunk_name"],
            "chunk_type": chunk["chunk_type"],
            "start_line": chunk["start_line"],
            "end_line": chunk["end_line"],
            "code": chunk["code"],
            "repo_owner": owner,
            "repo_name": repo,
            "branch": branch,
        }

        points.append(
            models.PointStruct(
                id=point_id,
                vector=vector,
                payload=payload,
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
        wait=True,
    )

    print(f"Indexed {len(points)} code chunks successfully.")


def search_chunks(question, limit=5):
    """Find the most relevant code chunks for a question."""

    if not client.collection_exists(COLLECTION_NAME):
        return []

    query_vector = embedding_model.encode(
        question,
        normalize_embeddings=True,
    ).tolist()

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=limit,
        with_payload=True,
    ).points

    return results
