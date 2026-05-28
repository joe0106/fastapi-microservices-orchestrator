import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent
mode = os.getenv("MODE", "")
env_file_name = f".env.{mode}" if mode else ".env"

class BasicSettings(BaseSettings):
    app_mode : str
    order_service_url: str
    inventory_service_url: str
    shipping_service_url: str
    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/{env_file_name}")

class Settings(BasicSettings):
    def service_map(self):
        return {
            "service-a": f"{self.order_service_url}/order",
            "service-b": f"{self.inventory_service_url}/items",
            "service-c": f"{self.shipping_service_url}/shipping"
        }
    def build_url(self, service: str, path: str):
        base_url = self.service_map().get(service)
        if not base_url:
            return None
        return f"{base_url.rstrip('/')}/{path.lstrip('/')}"

settings = Settings()