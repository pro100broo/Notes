"""
Uploading following constants to the database access via venv variables
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Database constants
HOST = os.environ.get("HOST")[::]
PORT = os.environ.get("PORT")[::]
USER = os.environ.get("USER")[::]
PASSWORD = os.environ.get("PASSWORD")[::]
DATA_BASE_NAME = os.environ.get("DATA_BASE_NAME")[::]

