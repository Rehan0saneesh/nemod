import os
from pydantic import BaseModel

class Settings(BaseModel):
    NEBIUS_API_KEY: str = os.getenv("NEBIUS_API_KEY", "")
    NEBIUS_BASE_URL: str = os.getenv("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1/")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    CLOUD_WORKER_URL: str = os.getenv("CLOUD_WORKER_URL", "http://localhost:8000")
    MODEL_NANO: str = "nvidia/nemotron-3-nano"
    MODEL_ULTRA: str = "nvidia/nemotron-3-ultra"

settings = Settings()