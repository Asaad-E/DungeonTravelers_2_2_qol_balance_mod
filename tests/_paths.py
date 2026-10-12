"""Shared locations for the test suite. Importing it makes tools importable."""
import os
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.join(PROJECT_DIR, 'tools')
BACKUP_DIR = os.path.join(PROJECT_DIR, 'backups')
TABLES_DIR = os.path.join(PROJECT_DIR, 'data_tables')

if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)
