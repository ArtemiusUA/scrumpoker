from functools import lru_cache
from pathlib import Path

from pydantic import BaseSettings
from starlette.templating import Jinja2Templates


class Settings(BaseSettings):
    secret_key: str = "test"
    redis_url: str = "redis://localhost"
    debug: bool = True


settings = Settings()
base_dir = Path(__file__).parent
templates = Jinja2Templates(directory=base_dir.joinpath("templates"))
