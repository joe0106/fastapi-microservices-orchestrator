import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent
mode = os.getenv("MODE", "")
env_file_name = f".env.{mode}" if mode else ".env"

class Settings(BaseSettings):
    app_mode : str
    order_service_url: str
    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/{env_file_name}")

settings = Settings()