"""
Database package for MCP QA.

This package provides database functionality for the MCP QA codebase,
including models, connection management, and query functionality.
"""

import os
from pathlib import Path

from mcp_qa.logging.logger import logger

from .db_manager import get_connection
from .repository import (
    save_test_results_to_db,
    save_source_file_to_db,
    save_test_file_to_db,
)
from .schema import execute_schema
from .crud.source_files import (
    create_source_file,
    get_source_file_by_id,
    get_source_file_by_path,
    update_source_file,
    delete_source_file,
    list_source_files,
)

# Define database directory with absolute path for reliability
DB_DIR = Path(__file__).parent / "data"


def init_database(db_name: str = "mcp_qa"):
    """
    Initialize database with all necessary tables.

    This function ensures the database directory exists and
    creates all tables defined in the schema file.

    Args:
        db_name: Name of the database file (without extension)
    """
    # Ensure the database directory exists
    DB_DIR.mkdir(parents=True, exist_ok=True)

    # Database file path
    db_path = DB_DIR / f"{db_name}.sqlite"

    logger.info(f"Initializing database at {db_path}")

    # Create connection with optimized settings
    connection = get_connection(db_name)

    # Execute the schema to create all tables
    execute_schema(connection)

    logger.info("Database initialization complete")


__all__ = [
    "save_test_results_to_db",
    "save_source_file_to_db",
    "save_test_file_to_db",
    "init_database",
    "create_source_file",
    "get_source_file_by_id",
    "get_source_file_by_path",
    "update_source_file",
    "delete_source_file",
    "list_source_files",
]
