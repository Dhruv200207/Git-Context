
from src.ingestion.github_loader import (
    get_repository_files,
    get_file_content,
)
from src.parsing.code_chunker import chunk_python_code
from src.retrieval.vector_store import (
    reset_collection,
    index_chunks,
)

MAX_FILES = 30
MAX_FILE_SIZE = 1_000_000


def index_repository(owner: str, repo: str) -> dict:
    """Fetch, chunk and index a GitHub repository."""

    owner = owner.strip()
    repo = repo.strip()

    if not owner or not repo:
        raise ValueError("GitHub owner and repository name are required.")

    print(f"\nLoading repository: {owner}/{repo}")

    files = get_repository_files(owner, repo)

    python_files = [
        item for item in files
        if item["path"].endswith(".py")
        and item["size"] <= MAX_FILE_SIZE
    ][:MAX_FILES]

    if not python_files:
        raise ValueError(
            "No suitable Python files found in this repository."
        )

    branch = python_files[0].get("branch", "main")
    all_chunks = []
    successful_files = 0
    failed_files = 0

    for number, item in enumerate(python_files, start=1):
        path = item["path"]
        file_branch = item.get("branch", branch)

        print(f"[{number}/{len(python_files)}] Processing {path}")

        try:
            source_code = get_file_content(
                owner, repo, path, file_branch
            )

            if not source_code or not source_code.strip():
                continue

            chunks = chunk_python_code(
                source_code=source_code,
                file_path=path,
                repo_owner=owner,
                repo_name=repo,
                branch=file_branch,
            )

            if chunks:
                all_chunks.extend(chunks)
                successful_files += 1

        except Exception as error:
            failed_files += 1
            print(f"Failed to process {path}: {error}")

    # Don't delete the old index if no chunks were created.
    if not all_chunks:
        raise ValueError(
            "No code chunks were created. The existing index was preserved."
        )

    # WARNING: This replaces the current indexed repository.
    reset_collection()
    index_chunks(all_chunks)

    return {
        "status": "success",
        "repository": f"{owner}/{repo}",
        "branch": branch,
        "files_selected": len(python_files),
        "files_processed": successful_files,
        "files_failed": failed_files,
        "chunks_created": len(all_chunks),
        "message": "Repository indexed successfully.",
    }


if __name__ == "__main__":
    owner = input("GitHub username or organization: ").strip()
    repo = input("Repository name: ").strip()

    try:
        result = index_repository(owner, repo)
        print(result)
    except Exception as error:
        print(f"Indexing failed: {error}")
