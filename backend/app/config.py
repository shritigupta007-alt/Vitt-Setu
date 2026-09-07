from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "VittSetu Prototype API"
    api_version: str = "0.1.0"
    allowed_origins: tuple[str, ...] = (
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    )


def get_settings() -> Settings:
    configured_origins = os.getenv("ALLOWED_ORIGINS")
    if not configured_origins:
        return Settings()

    origins = tuple(origin.strip() for origin in configured_origins.split(",") if origin.strip())
    return Settings(allowed_origins=origins or Settings.allowed_origins)
