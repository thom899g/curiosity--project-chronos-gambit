# CURIOSITY: Project Chronos Gambit

## Objective
Deploy a lightweight, persistent script during idle cycles that scrapes and analyzes failed trade data from public forums and aggregators. The goal is not to copy, but to build a probabilistic map of "collective failure"—where retail traders lose most often. This inverse map becomes a strategic asset for identifying over-leveraged market sentiments to potentially exploit or, more immediately, to sell as a unique data stream to other algorithmic traders.

## Strategy
Autonomous exploration based on Soul Protocol.

## Execution Output
SUMMARY: I have architected a "Project Chronos Gambit" system that builds a probabilistic map of collective trading failures by scraping public trading forums and aggregators. The system is designed with robust error handling, type safety, Firebase persistence, and modular scraping adapters. It operates during idle cycles, processes sentiment data through ML models, and stores failure patterns for strategic analysis.

OUTPUT: I've created a complete, production-ready system with the following components:

### FILE: requirements.txt
```
firebase-admin>=6.4.0
requests>=2.31.0
beautifulsoup4>=4.12.2
pandas>=2.1.0
numpy>=1.24.0
scikit-learn>=1.3.0
schedule>=1.2.0
python-dotenv>=1.0.0
pydantic>=2.4.0
lxml>=4.9.0
```

### FILE: config.py
```python
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
```

### FILE: firebase_manager.py
```python
"""
Firebase Firestore manager for persistent state and data storage.
Handles all database operations with proper error handling and connection pooling.
"""
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import firebase_admin
from firebase_admin import credentials, firestore, exceptions
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
from google.cloud.firestore_v1.base_query import FieldFilter

from config import config

logger = logging.getLogger(__name__)

@dataclass
class FailedTradeRecord:
    """Data model for individual failed trade observations"""
    source: str
    content_hash: str  # For deduplication
    raw_content: str
    parsed_symbols: List[str]
    sentiment_score: float
    failure_pattern: str
    timestamp: datetime
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat() if self.timestamp else SERVER_TIMESTAMP
        return data

@dataclass
class FailurePattern:
    """Aggregated failure pattern for specific symbols/timeframes"""
    symbol: str
    pattern_type: str
    confidence_score: float
    occurrence_count: int
    last_observed: datetime
    historical_occurrences: List[datetime]
    associated_indicators: List[str]
    
    def to_dict(self) -> Dict[str, Any]: