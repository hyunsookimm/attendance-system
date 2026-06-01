from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    env: str = "production"
    allowed_origins: str = ""

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    model_config = {"env_file": ".env"}


settings = Settings()  # type: ignore[call-arg]
