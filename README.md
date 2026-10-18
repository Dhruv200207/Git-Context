
# GitContext — AI-Powered Codebase Intelligence

GitContext is an AI-powered developer copilot that helps developers understand Python codebases through natural-language questions. It retrieves relevant code using semantic search and generates contextual answers with GitHub source links.

## Features

- **GitHub Repository Ingestion:** Fetch Python source files from a GitHub repository.
- **Intelligent Code Chunking:** Split Python code into functions, classes, and modules.
- **Semantic Search:** Retrieve relevant code using vector embeddings.
- **AI-Powered Explanations:** Generate answers grounded in retrieved code context.
- **Source References:** Display GitHub links to relevant files and line ranges.
- **Repository Indexing:** Index a selected repository through the Streamlit interface.
- **REST API:** Expose codebase question-answering through FastAPI.
- **Interactive Dashboard:** Ask questions and inspect indexing results through Streamlit.

## Architecture

```text
GitHub Repository
       |
       v
GitHub Loader
       |
       v
Python Code Chunker
       |
       v
Sentence Transformers
       |
       v
Qdrant Vector Database
       |
       v
Semantic Retrieval
       |
       v
Groq LLM
       |
       v
Answer + GitHub Sources
       |
       v
Streamlit Dashboard
```

FastAPI provides the backend endpoints for repository indexing and question answering.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core development |
| Streamlit | Interactive user interface |
| FastAPI | Backend REST API |
| Qdrant | Vector storage and similarity search |
| Sentence Transformers | Code embeddings |
| Groq API | LLM-powered answers |
| GitHub REST API | Repository and source-file retrieval |
| Pydantic | Request validation |

## Project Structure

```text
GitContext/
├── app.py
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
└── src/
    ├── api/
    │   └── main.py
    ├── ingestion/
    │   ├── github_loader.py
    │   └── indexer.py
    ├── parsing/
    │   └── code_chunker.py
    └── retrieval/
        ├── vector_store.py
        ├── search.py
        └── answer_generator.py
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/GitContext.git
cd GitContext
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root using `.env.example` as a template.

```env
GROQ_API_KEY=your_groq_api_key
GITHUB_TOKEN=your_github_token
```

Use a GitHub token only if required for your repository access or API rate limits. Never commit `.env` or expose API keys publicly.

### 5. Start the FastAPI backend

```bash
python -m uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000
```

API documentation:

http://127.0.0.1:8000/docs

Health endpoint:

http://127.0.0.1:8000/health

### 6. Start the Streamlit frontend

Open a second terminal in the project folder and run:

```bash
python -m streamlit run app.py
```

### 7. Index a repository

Enter the GitHub owner and repository name in the Repository Manager, confirm the index replacement warning, and start indexing.

**Note:** The current implementation indexes up to 30 Python files, with a maximum file size of 1 MB per file. Indexing a new repository replaces the existing Qdrant collection.

## How It Works

1. GitContext retrieves Python files from a GitHub repository.
2. The code parser creates searchable chunks.
3. Sentence Transformers converts code chunks into embeddings.
4. Qdrant stores the vectors and associated source metadata.
5. A user submits a natural-language question.
6. Semantic search retrieves relevant code chunks.
7. Groq generates an answer using the retrieved context.
8. GitHub source links help the user inspect the referenced code.

## Example Questions

- How does request validation work in this repository?
- Explain the main functions in a particular Python module.
- How is the API structured?
- Which code handles repository indexing?
- Where is a particular function defined?

Answers depend on the code successfully retrieved from the indexed repository.

## Current Limitations

- Python files are currently the primary indexing target.
- The index is designed for one active repository at a time.
- Large repositories are limited by the configured file-count and file-size caps.
- Answer quality depends on retrieval quality, available source context, and LLM availability.
- Local Qdrant storage requires a suitable persistent environment.

## Security

- Keep API keys in environment variables.
- Never commit `.env` or private credentials.
- Use repositories you are authorized to access.
- Review retrieved code before using AI-generated recommendations.

## Future Improvements

- Live indexing progress and job status
- Support for additional programming languages
- Repository-aware filtering and multiple indexes
- Automated tests and CI workflows
- Improved retrieval evaluation
- Production deployment with persistent vector storage

## Author

**YOUR NAME**

GitHub: https://github.com/YOUR_USERNAME

---

*GitContext is a learning and portfolio project exploring retrieval-augmented generation (RAG), vector search, code parsing, and AI-assisted software development.*
