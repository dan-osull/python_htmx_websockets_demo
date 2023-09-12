import logging
from pathlib import Path

SQLITE_DB_DIR = Path.cwd() / "db_files"
SQLITE_DB_DIR.mkdir(exist_ok=True)
SQLITE_DB_URL = "sqlite:///" + str(SQLITE_DB_DIR / "db.sqlite")
TEMPLATES_PATH = Path.cwd() / Path("src") / "templates"
LOG_LEVEL = logging.INFO
