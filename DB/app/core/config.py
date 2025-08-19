from pydantic import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MONGO_URL: str
    MONGO_DB_NAME: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()