"""
Configuration management for the ATS API.

This file loads environment variables from a `.env` file and makes them
available for use throughout the application.
"""

import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# --- Database Configuration ---
DATABASE_URL = os.getenv("DATABASE_URL")

# --- JWT Authentication Configuration ---
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
