from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str
    threshold: float
    log_dir: str

    class Config:
        env_file = ".env"


settings = Settings()
