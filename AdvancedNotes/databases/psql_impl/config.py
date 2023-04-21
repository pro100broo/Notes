"""
Uploading following constants to the database access via venv variables
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Database constants
PSQL_HOST = os.environ.get("PSQL_HOST")[::]
PSQL_PORT = os.environ.get("PSQL_PORT")[::]
PSQL_USER = os.environ.get("PSQL_USER")[::]
PSQL_PASSWORD = os.environ.get("PSQL_PASSWORD")[::]
PSQL_DATA_BASE_NAME = os.environ.get("PSQL_DATA_BASE_NAME")[::]

