import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DIFY_API_URL: str = os.getenv("DIFY_API_URL")
    DIFY_API_KEY: str = os.getenv("DIFY_API_KEY")


settings = Settings()


def get_params_dify():
    return {"dify_api_url": settings.DIFY_API_URL, "dify_api_key": settings.DIFY_API_KEY}