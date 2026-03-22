from typing import Literal, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import lru_cache

Environment = Literal["local", "dev", "staging", "prod"]
RetrieverBackend = Literal["vertex_rag_engine", "vertex_ai_search", "custom_api"]

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        env_prefix="APP_",)
    
    name: str = "multi-agent-rag"
    env: Environment = "local"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8080

class GoogleSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        env_prefix="GOOGLE_",)
    
    cloud_project: str
    cloud_location: str
    genai_use_vertexai: bool = True

class ModelSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        env_prefix="MODEL_",)
    planner_model: str = "gemini-2.5-flash"
    answer_model: str = "gemini-2.5-pro"
    verifier_model: str = "gemini-2.5-flash"
    triage_model: str = "gemini-2.5-flash"
    drafting_model: str = "gemini-2.5-flash"
    root_model: str = "gemini-2.5-flash"
    temperature: float = Field(default=0.2, ge=0, le=2)
    max_output_tokens: int = Field(default=2048, ge=128, le=8192)
    router_model: Optional[str] = None
    rerank_model: Optional[str] = None
    safety_model: Optional[str] = None
    timeout_seconds: Optional[int] = Field(default=None, ge=1, le=300)
    max_retries: Optional[int] = Field(default=None, ge=0, le=10)

class RetrievalSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        env_prefix="RAG_",)
    backend: RetrieverBackend = "vertex_rag_engine"
    top_k: int = Field(default=10, ge=8, le=20)
    max_context_chunks: int = Field(default=6, ge=4, le=10)
    enable_rerank: bool = True
    rag_corpus: Optional[str] = None
    vertex_search_datastore: Optional[str] = None
    retriever_api_base_url: Optional[str] = None 

@lru_cache(maxsize=1)
def get_app_settings() -> AppSettings:
    return AppSettings()

@lru_cache(maxsize=1)
def get_google_settings() -> GoogleSettings:
    return GoogleSettings()

@lru_cache(maxsize=1)
def get_model_settings() -> ModelSettings:
    return ModelSettings()

@lru_cache(maxsize=1)
def get_retrieval_settings() -> RetrievalSettings:
    return RetrievalSettings()
