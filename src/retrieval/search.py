
from src.retrieval.vector_store import search_chunks


def search_repository(question, limit=5):
    """Find code chunks relevant to a natural-language question."""

    if not question.strip():
        print("Please enter a question.")
        return

    try:
        results = search_chunks(question, limit=limit)

        if not results:
            print("No matching code found.")
            return

        print("\n" + "=" * 60)
        print("GITCONTEXT - SEARCH RESULTS")
        print("=" * 60)

        for rank, result in enumerate(results, start=1):
            payload = result.payload or {}

            print(f"\nResult #{rank}")
            print(f"File: {payload.get('file_path', 'Unknown')}")
            print(f"Name: {payload.get('chunk_name', 'Unknown')}")
            print(
                f"Lines: {payload.get('start_line', '?')}"
                f"-{payload.get('end_line', '?')}"
            )
            print(f"Similarity score: {result.score:.4f}")
            print("-" * 40)
            print(payload.get("code", "No code available"))
            print("-" * 60)

    except Exception as error:
        print(f"Search failed: {error}")


if __name__ == "__main__":
    print("GitContext - Codebase Semantic Search")
    print("Ask a question about the indexed repository.")
    print("Type 'exit' to quit.")

    while True:
        question = input("\nYour question: ").strip()

        if question.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        search_repository(question)
