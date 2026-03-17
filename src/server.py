from fastapi import FastAPI
from src.api import router

def creat_app() -> FastAPI:
    app = FastAPI(
        title="Google ADK RAG API",
        version="0.1.0")
    app.include_router(router)
    return app

app = creat_app()
    

