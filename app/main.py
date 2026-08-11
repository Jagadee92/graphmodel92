from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import public_router, protected_router

app = FastAPI(
    title="TalentGraph API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(public_router)
app.include_router(protected_router)


@app.get("/")
def root():
    return {
        "message": "TalentGraph API is running",
        "status": "success"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }