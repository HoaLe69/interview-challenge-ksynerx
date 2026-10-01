import os 

from dotenv import load_dotenv

load_dotenv();

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://cdms:cdms@db:5432/cdms"
)

POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "300"))
