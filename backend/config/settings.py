"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "Debbie's Travel Agent Assistant"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "change-this-in-production"

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Gmail API
    GMAIL_CLIENT_ID: str
    GMAIL_CLIENT_SECRET: str
    GMAIL_REFRESH_TOKEN: Optional[str] = None

    # Twilio SMS
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str

    # Alert Configuration
    ALERT_EMAIL: str
    ALERT_SMS: str
    SECONDARY_EMAIL: Optional[str] = None
    SECONDARY_SMS: Optional[str] = None

    # Travel API Keys
    AMADEUS_API_KEY: Optional[str] = None
    AMADEUS_API_SECRET: Optional[str] = None

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None

    # Social Media APIs
    TWITTER_BEARER_TOKEN: Optional[str] = None
    REDDIT_CLIENT_ID: Optional[str] = None
    REDDIT_CLIENT_SECRET: Optional[str] = None
    REDDIT_USER_AGENT: str = "DebbieTA/1.0"

    # Deal Thresholds (in cents for cash, points for miles)
    ASIA_MILES_THRESHOLD: int = 60000
    ASIA_CASH_THRESHOLD: int = 100000  # $1000 in cents
    EUROPE_MILES_THRESHOLD: int = 30000
    EUROPE_CASH_THRESHOLD: int = 70000  # $700 in cents

    # Default Airport
    DEFAULT_AIRPORT: str = "MSP"

    # RSS Feeds
    RSS_FEEDS: str = "https://thepointsguy.com/feed/,https://www.thriftytraveler.com/feed/"
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    # Task Intervals (in hours)
    DEAL_CHECK_INTERVAL: int = 12
    RSS_CHECK_INTERVAL: int = 6
    EMAIL_SCAN_INTERVAL: int = 1

    # Airlines & Hotels of Interest
    PREFERRED_AIRLINES: List[str] = [
        "Delta", "DL", "American", "AA", "United", "UA",
        "Air France", "AF", "KLM", "KL", "Virgin Atlantic", "VS"
    ]

    PREFERRED_HOTEL_CHAINS: List[str] = [
        "Marriott", "Hyatt", "Hilton", "IHG", "Melia",
        "Ritz-Carlton", "St. Regis", "W Hotels"
    ]

    PREFERRED_CRUISE_LINES: List[str] = [
        "Viking", "Royal Caribbean", "Celebrity", "Regent Seven Seas",
        "Oceania", "Seabourn", "Cunard"
    ]

    # Loyalty Programs
    LOYALTY_PROGRAMS: dict = {
        "delta": "SkyMiles",
        "marriott": "Bonvoy",
        "hyatt": "World of Hyatt",
        "chase": "Ultimate Rewards",
        "amex": "Membership Rewards"
    }

    # Legal Research Sources
    LEGAL_SOURCES: List[str] = [
        "https://www.transportation.gov/airconsumer/fly-rights",
        "https://www.ecfr.gov/current/title-14/chapter-II/subchapter-A/part-259",
        "https://europa.eu/youreurope/citizens/travel/passenger-rights/air/index_en.htm"
    ]

    # Travel Deal Sites (RSS)
    TRAVEL_DEAL_SITES: List[dict] = [
        {"name": "The Points Guy", "url": "https://thepointsguy.com/feed/"},
        {"name": "Thrifty Traveler", "url": "https://www.thriftytraveler.com/feed/"},
        {"name": "Going (formerly Scott's Cheap Flights)", "url": "https://going.com/feed/"},
        {"name": "Secret Flying", "url": "https://www.secretflying.com/feed/"},
        {"name": "Fly4Free", "url": "https://www.fly4free.com/feed/"}
    ]

    # Social Media Sources for Dispute Research
    SOCIAL_MEDIA_SOURCES: dict = {
        "reddit": [
            "r/delta", "r/awardtravel", "r/travel", "r/churning",
            "r/marriott", "r/hyatt", "r/flights"
        ],
        "flyertalk": [
            "https://www.flyertalk.com/forum/delta-air-lines-skymiles/",
            "https://www.flyertalk.com/forum/american-airlines-aadvantage/",
            "https://www.flyertalk.com/forum/marriott-bonvoy/"
        ]
    }

    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000"
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Export settings instance
settings = get_settings()
