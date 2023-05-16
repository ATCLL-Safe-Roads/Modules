from pydantic import BaseSettings


class Settings(BaseSettings):
    # ATCLL Settings
    ATCLL_BROKER_HOST: str
    ATCLL_BROKER_PORT: int
    # OpenWeather Settings
    OPENWEATHER_API_KEY: str
    OPENWEATHER_HISTORY_URL: str
    # MongoDB Settings
    MONGO_DATABASE: str
    DATABASE_URL: str

    class Config:
        env_file = '.env'


settings = Settings()
