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