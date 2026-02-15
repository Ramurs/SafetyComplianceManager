from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Anthropic
    anthropic_api_key: str = ""

    # Azure / Office 365
    azure_tenant_id: str = ""
    azure_client_id: str = ""
    azure_client_secret: str = ""

    # Database
    database_url: str = f"sqlite+aiosqlite:///{BASE_DIR / 'data' / 'scm.db'}"

    # Application
    app_env: str = "development"
    log_level: str = "INFO"
    agent_max_iterations: int = 20
    agent_max_tokens: int = 4096

    @property
    def data_dir(self) -> Path:
        return BASE_DIR / "data"

    @property
    def templates_dir(self) -> Path:
        return self.data_dir / "templates"

    @property
    def frameworks_dir(self) -> Path:
        return self.data_dir / "frameworks"

    @property
    def output_dir(self) -> Path:
        d = self.data_dir / "output"
        d.mkdir(parents=True, exist_ok=True)
        return d


def get_settings() -> Settings:
    return Settings()
