"""
Temporary configuration file.
I am planning to create a separate class to dynamically maneged app settings
"""
import os

from dotenv import load_dotenv

load_dotenv()

# Database constants
JSON_PATH = os.environ.get("JSON_PATH")[::]
HOST = os.environ.get("HOST")[::]
PORT = os.environ.get("PORT")[::]
USER = os.environ.get("USER")[::]
PASSWORD = os.environ.get("PASSWORD")[::]

# Syntax settings
COLORFUL_SYNTAX = True

# Text redactor settings
AUTO_COMPLETION = True
TOOLBAR = True
LINE_SYMBOL = ">>> "

# Table view settings
HORIZONTAL_TABLE_CHAR = "="
JUNCTION_TABLE_CHER = "O"

