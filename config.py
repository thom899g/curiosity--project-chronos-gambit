"""
Configuration manager with environment variable validation.
Uses Pydantic for robust type validation and environment parsing.
"""
import os
from typing import Optional, Dict, Any
from pydantic import BaseSettings, Field, validator
from dotenv import load_dotenv

load_dotenv()

class ChronosConfig(BaseSettings):
    """Configuration for Project Chronos Gambit"""
    
    # Firebase Configuration
    firebase_project_id: str = Field(..., env="FIREBASE_PROJECT_ID")
    firebase_credentials_path: str = Field("./firebase-credentials.json", env="FIREBASE_CREDS_PATH")
    
    # Scraping Configuration
    scraping_interval_minutes: int = Field(30, env="SCRAPING_INTERVAL_MINUTES")
    max_scraping_threads: int = Field(3, env="MAX_SCRAPING_THREADS")
    request_timeout_seconds: int = Field(10, env="REQUEST_TIMEOUT_SECONDS")
    user_agent: str = Field(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        env="USER_AGENT"
    )
    
    # Rate Limiting
    requests_per_minute: int = Field(20, env="REQUESTS_PER_MINUTE")
    delay_between_requests: float = Field(3.0, env="DELAY_BETWEEN_REQUESTS")
    
    # Data Processing
    min_samples_for_model: int = Field(100, env="MIN_SAMPLES_FOR_MODEL")
    failure_threshold_percentile: float = Field(0.75, env="FAILURE_THRESHOLD_PERCENTILE")
    
    # Telegram Alerting
    telegram_bot_token: Optional[str] = Field(None, env="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: Optional[str] = Field(None, env="TELEGRAM_CHAT_ID")
    
    # Data Sources (comma-separated URLs)
    forum_urls: str = Field(
        "https://www.reddit.com/r/wallstreetbets,https://www.tradingview.com/ideas",
        env="FORUM_URLS"
    )
    
    @validator('firebase_credentials_path')
    def validate_firebase_creds(cls, v):
        if not os.path.exists(v):
            raise FileNotFoundError(f"Firebase credentials file not found at {v}")
        return v
    
    @validator('scraping_interval_minutes')
    def validate_interval(cls, v):
        if v < 5:
            raise ValueError("Scraping interval must be at least 5 minutes")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False

def get_config() -> ChronosConfig:
    """Get validated configuration instance"""
    return ChronosConfig()

config = get_config()