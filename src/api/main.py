
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.ingestion.indexer import index_repository
from src.retrieval.answer_generator import generate_answer

app = FastAPI(
    title="GitContext API",
    description="AI-powered GitHub codebase assistant",
    version="1.1.0",
)


class QuestionRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)


class AnswerResponse(BaseModel):
    question: str
    answer: str


class RepositoryRequest(BaseModel):
    owner: str = Field(min_length=1, max_length=100)
    repo: str = Field(min_length=1, max_length=100)


@app.get("/")
def home():
    return {
        "message": "GitContext API is running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    try:
        answer = generate_answer(request.question)

        if answer.startswith(
            ("Code search failed:", "AI answer generation failed:")
        ):
            raise HTTPException(status_code=502, detail=answer)

        return AnswerResponse(
            question=request.question,
            answer=answer,
        )

    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Could not answer the question: {error}",
        )


@app.post("/index")
def index_github_repository(request: RepositoryRequest):
    try:
        return index_repository(
            request.owner,
            request.repo,
        )

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Repository indexing failed: {error}",
        )
