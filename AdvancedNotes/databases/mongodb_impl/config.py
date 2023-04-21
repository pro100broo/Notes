"""
Uploading following constants to the database access via venv variables
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Database constants
MongoDB_HOST = os.environ.get("MongoDB_HOST")[::]
MongoDB_PORT = os.environ.get("MongoDB_PORT")[::]
