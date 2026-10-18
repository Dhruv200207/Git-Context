
import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_API_URL = "https://api.github.com"

# Maximum size of a file we will download in this step.
MAX_FILE_SIZE = 1_000_000

# File types we want to index initially.
ALLOWED_EXTENSIONS = {
    ".py", ".js", ".ts", ".java", ".sql",
    ".html", ".css", ".md", ".json", ".yaml", ".yml"
}


def get_headers():
    token = os.getenv("GITHUB_TOKEN")

    headers = {
        "Accept": "application/vnd.github+json"
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    return headers


def get_repository_files(owner, repo):
    """Return supported file metadata from a repository."""

    headers = get_headers()

    repo_url = f"{GITHUB_API_URL}/repos/{owner}/{repo}"

    response = requests.get(
        repo_url,
        headers=headers,
        timeout=20
    )
    response.raise_for_status()

    repository_data = response.json()
    default_branch = repository_data["default_branch"]

    tree_url = (
        f"{GITHUB_API_URL}/repos/{owner}/{repo}"
        f"/git/trees/{default_branch}?recursive=1"
    )

    tree_response = requests.get(
        tree_url,
        headers=headers,
        timeout=30
    )
    tree_response.raise_for_status()

    tree_data = tree_response.json()

    if tree_data.get("truncated", False):
        print("Warning: GitHub returned a truncated file tree.")

    files = []

    for item in tree_data.get("tree", []):
        if item.get("type") != "blob":
            continue

        path = item["path"]
        extension = os.path.splitext(path)[1].lower()

        # Skip files outside our supported extensions.
        if extension not in ALLOWED_EXTENSIONS:
            continue

        files.append({
            "path": path,
            "sha": item["sha"],
            "size": item.get("size", 0),
            "branch": default_branch
        })

    return files


def get_file_content(owner, repo, path, branch):
    """Download and decode one supported text file."""

    headers = get_headers()

    # Avoid requesting files that exceed our configured size limit.
    # The caller supplies size metadata from the repository tree.
    # Size is checked there before this function is called.

    encoded_path = requests.utils.quote(path, safe="/")

    file_url = (
        f"{GITHUB_API_URL}/repos/{owner}/{repo}"
        f"/contents/{encoded_path}"
    )

    response = requests.get(
        file_url,
        headers=headers,
        params={"ref": branch},
        timeout=30
    )
    response.raise_for_status()

    file_data = response.json()

    if isinstance(file_data, list):
        raise ValueError("Expected a file, but received a directory.")

    if file_data.get("encoding") != "base64":
        raise ValueError(
            "GitHub did not return base64 content for this file."
        )

    encoded_content = file_data["content"]

    decoded_bytes = base64.b64decode(encoded_content)

    # Decode text safely; skip files that are not valid UTF-8 text.
    try:
        content = decoded_bytes.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("File is not valid UTF-8 text.") from error

    return content


def main():
    """Test repository listing and file-content retrieval."""

    owner = input("GitHub username or organization: ").strip()
    repo = input("Repository name: ").strip()

    try:
        files = get_repository_files(owner, repo)

        print(f"\nFound {len(files)} supported files.")

        # Keep this test small to avoid unnecessary API requests.
        for file_info in files[:10]:
            print(f"\nFile: {file_info['path']}")
            print(f"Size: {file_info['size']} bytes")

            if file_info["size"] > MAX_FILE_SIZE:
                print("Skipped: file exceeds the size limit.")
                continue

            try:
                content = get_file_content(
                    owner,
                    repo,
                    file_info["path"],
                    file_info["branch"]
                )

                print("Content preview:")
                print(content[:500])

                if len(content) > 500:
                    print("... preview shortened ...")

            except (requests.RequestException, ValueError) as error:
                print(f"Could not read this file: {error}")

    except requests.RequestException as error:
        print(f"GitHub request failed: {error}")
    except (KeyError, ValueError) as error:
        print(f"Could not process repository response: {error}")


if __name__ == "__main__":
    main()
