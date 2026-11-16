from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    database_url: str = 'postgresql+psycopg://supportpilot:supportpilot@localhost:5432/supportpilot'
    model_dir: Path = Path('models')
    sentiment_dir: Path = Path('models/sentiment')
    sentiment_enabled: bool = True
    sentiment_model: str = 'cardiffnlp/twitter-roberta-base-sentiment-latest'
    sentiment_revision: str = '3216a57f2a0d9c45a2e6c20157c20c49fb4bf9c7'
    ollama_url: str = 'http://localhost:11434'
    ollama_model: str = 'llama3.2:3b'
    inference_threshold: float = Field(default=0.60, ge=0, le=1)
    cors_origins: list[str] = ['http://localhost:5174', 'http://127.0.0.1:5174']


settings = Settings()
