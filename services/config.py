import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(dotenv_path=BASE_DIR / ".env")

class Config:
    """Centralized configuration management for Tiffany Bot."""
    
    DISCORD_BOT_TOKEN: str = os.getenv("DISCORD_BOT_TOKEN", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development").lower()
    
    # Paths
    DATA_DIR: Path = BASE_DIR / "data"
    LOG_FILE: Path = DATA_DIR / "bot.log"
    
    @classmethod
    def validate(cls) -> None:
        """Validates that critical configurations are present."""
        if not cls.DISCORD_BOT_TOKEN:
            raise ValueError(
                "CRITICAL ERROR: DISCORD_BOT_TOKEN is not set in the environment or .env file.\n"
                "Please copy .env.example to .env and fill in your credentials."
            )
        
        # Ensure directories exist
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
