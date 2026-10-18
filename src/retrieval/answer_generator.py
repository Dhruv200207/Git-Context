
import os
from pathlib import Path
from urllib.parse import quote

from dotenv import load_dotenv
from groq import Groq

from src.retrieval.vector_store import search_chunks

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE, override=True)


def generate_answer(question: str) -> str:
    """Generate a grounded answer with GitHub source links."""

    if not question or not question.strip():
        return "Please enter a question about the indexed codebase."

    api_key = os.getenv("GROQ_API_KEY", "").strip()

    if not api_key:
        return "GROQ_API_KEY is missing. Check your .env file."

    try:
        results = search_chunks(question, limit=5)

        if not results:
            return (
                "No indexed code was found. Run the repository indexer "
                "before asking questions."
            )

        context_parts = []
        source_parts = []
        seen_sources = set()

        for index, result in enumerate(results, start=1):
            payload = result.payload or {}

            file_path = payload.get("file_path", "Unknown file")
            chunk_name = payload.get("chunk_name", "Unknown symbol")
            start_line = payload.get("start_line", 1)
            end_line = payload.get("end_line", start_line)
            code = payload.get("code", "")

            context_parts.append(
                f"[Source {index}]\n"
                f"File: {file_path}\n"
                f"Symbol: {chunk_name}\n"
                f"Lines: {start_line}-{end_line}\n"
                f"Code:\n{code}"
            )

            owner = payload.get("repo_owner", "")
            repo = payload.get("repo_name", "")
            branch = payload.get("branch", "")

            source_key = (
                owner, repo, branch, file_path, start_line, end_line
            )

            if source_key in seen_sources:
                continue

            seen_sources.add(source_key)

            if owner and repo and branch:
                safe_owner = quote(owner, safe="")
                safe_repo = quote(repo, safe="")
                safe_branch = quote(branch, safe="/")
                safe_path = quote(file_path, safe="/")

                github_url = (
                    f"https://github.com/{safe_owner}/{safe_repo}/blob/"
                    f"{safe_branch}/{safe_path}"
                    f"#L{start_line}-L{end_line}"
                )

                source_parts.append(
                    f"- [`{file_path}` (lines {start_line}-{end_line})]"
                    f"({github_url})"
                )
            else:
                source_parts.append(
                    f"- `{file_path}` — lines {start_line}-{end_line} "
                    "(GitHub link unavailable: metadata missing)"
                )

        context = "\n\n".join(context_parts)
        sources = "\n".join(source_parts) or "- No source references available."

        client = Groq(api_key=api_key)

        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are GitContext, an AI codebase assistant. "
                        "Answer using the supplied code context. Explain "
                        "clearly and accurately. If the context is "
                        "insufficient, say so. Never invent files, "
                        "functions, or line numbers. Cite relevant chunks "
                        "using labels such as [Source 1]."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Question:\n{question}\n\n"
                        f"Retrieved code context:\n{context}"
                    ),
                },
            ],
            temperature=0.2,
        )

        answer = completion.choices[0].message.content or (
            "The AI returned an empty answer."
        )

        return (
            f"{answer.strip()}\n\n"
            f"---\n"
            f"**Sources retrieved**\n\n"
            f"{sources}"
        )

    except Exception as error:
        return f"AI answer generation failed: {error}"


if __name__ == "__main__":
    question = input("Ask about the indexed codebase: ").strip()
    print("\n" + generate_answer(question))
