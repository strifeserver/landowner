"""
Database configuration module.
Centralizes DB_PATH for all models.
"""
import os
from utils.paths import DATA_DIR

# Database path handling using centralized DATA_DIR
DB_PATH = os.path.join(DATA_DIR, "data.db")

