from pydantic import BaseSettings


class Settings(BaseSettings):
    # ATCLL Settings
    ATCLL_BROKER_HOST: str
    ATCLL_BROKER_PORT: int
    # MongoDB Settings
    MONGO_DATABASE: str
    DATABASE_URL: str

    class Config:
        env_file = '.env'


settings = Settings()
