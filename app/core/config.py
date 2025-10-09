from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache

class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "AI Recipe Recommendation System"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # Security Settings
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # CORS Settings
    ALLOWED_ORIGINS_STR: str = "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000"
    
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS_STR.split(",")]
    
    # Database Settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "recipe_recommendation_db"
    
    # AI Model Settings
    GEMINI_API_KEY: str = "your-gemini-api-key-here"
    
    # Google Cloud Vision API - ADD THESE LINES
    GOOGLE_VISION_CREDENTIALS_PATH: str = ""
    ENABLE_VISION_API: bool = False
    VISION_API_MONTHLY_LIMIT: int = 166
    
    # Model Configuration
    MODEL_CONFIDENCE_THRESHOLD: float = 0.5
    MAX_INGREDIENTS_DETECTED: int = 10
    MAX_RECIPE_GENERATION_RETRIES: int = 3
    
    # File Upload Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024
    UPLOAD_DIR: str = "./uploads"
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    
    # Optional Features
    ENABLE_EMAIL_NOTIFICATIONS: bool = False
    ENABLE_ANALYTICS: bool = True
    ENABLE_BATCH_PROCESSING: bool = True
    ENABLE_RECIPE_CACHING: bool = True
    ENABLE_USER_RECOMMENDATIONS: bool = True
    ENABLE_MOOD_ANALYSIS: bool = True
    
    # Performance Settings
    MAX_CONCURRENT_REQUESTS: int = 100
    REQUEST_TIMEOUT: int = 30
    DATABASE_CONNECTION_TIMEOUT: int = 10
    
    # Development
    MOCK_AI_RESPONSES: bool = False
    MOCK_INGREDIENT_DETECTION: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    return Settings()