from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "E-Commerce Support Assistant"
    debug: bool = True
    database_url: str

    secret_key: str
    algorithm: str = "HS256"
    groq_api_key: str

    test_admin_email: str = ""
    test_admin_password: str = ""

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()