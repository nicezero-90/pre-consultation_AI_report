import os
from pydantic import BaseSettings
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

class Settings(BaseSettings):
    """應用程式設定"""
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # 應用程式設定
    APP_NAME: str = "檔案處理API"
    
    class Config:
        env_file = ".env"

settings = Settings()
