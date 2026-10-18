
import ast


def chunk_python_code(
    source_code: str,
    file_path: str,
    repo_owner: str = "",
    repo_name: str = "",
    branch: str = "main",
):
    """Split Python source into top-level functions and classes."""

    try:
        tree = ast.parse(source_code)
    except (SyntaxError, ValueError):
        return []

    lines = source_code.splitlines()
    chunks = []

    for node in tree.body:
        if not isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
        ):
            continue

        start_line = node.lineno
        end_line = getattr(node, "end_lineno", start_line)
        code = "\n".join(lines[start_line - 1:end_line]).strip()

        if not code:
            continue

        if isinstance(node, ast.ClassDef):
            chunk_type = "class"
        elif isinstance(node, ast.AsyncFunctionDef):
            chunk_type = "async_function"
        else:
            chunk_type = "function"

        chunks.append({
            "file_path": file_path,
            "chunk_name": node.name,
            "chunk_type": chunk_type,
            "start_line": start_line,
            "end_line": end_line,
            "code": code,
            "repo_owner": repo_owner,
            "repo_name": repo_name,
            "branch": branch,
        })

    # If the file has no top-level function/class, index the whole file
    # as one chunk so module-level code is not lost.
    if not chunks and source_code.strip():
        chunks.append({
            "file_path": file_path,
            "chunk_name": file_path.rsplit("/", 1)[-1],
            "chunk_type": "module",
            "start_line": 1,
            "end_line": max(1, len(lines)),
            "code": source_code.strip(),
            "repo_owner": repo_owner,
            "repo_name": repo_name,
            "branch": branch,
        })

    return chunks
