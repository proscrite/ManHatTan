from pydantic_settings import BaseSettings, SettingsConfigDict

import os

class Settings(BaseSettings):
    # Pydantic will automatically look for these keys in the environment or .env file.
    # It is case-insensitive by default, so 'secret_key' maps to 'SECRET_KEY'.
    secret_key: str
    db_password: str = "" 
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080
    database_url: str = "sqlite:///Users/pabloherrero/Documents/ManHatTan/mht/backend/app/manhattan.db"
    
    # In Pydantic v2, we configure the env file behavior via model_config
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore" # This explicitly tells Pydantic to ignore extra env variables it doesn't recognize
    )

# Instantiate a global settings object to be imported across the app
settings = Settings()