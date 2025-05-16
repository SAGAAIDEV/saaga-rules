"""
Database manager for MCP QA.

This module provides functionality for database connection management,
initialization, and schema management for SQLite database access
using raw sqlite3 instead of SQLModel.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, Generator, Optional, Tuple

from src.mcp_qa.config.env import PATHS
from src.mcp_qa.db.schema import execute_schema

# Cache connections to avoid recreating them
_CONNECTION_CACHE: Dict[str, sqlite3.Connection] = {}

# Use DB_DIR from env config
DB_DIR = PATHS.DB_DIR


def get_connection(
    name: str,
    timeout: float = 10.0,
    isolation_level: Optional[str] = None,
) -> sqlite3.Connection:
    """
    Get or create a database connection.

    Args:
        name: Name of the database
        timeout: Timeout for waiting for the database lock (seconds)
        isolation_level: SQLite isolation level (None for autocommit)

    Returns:
        SQLite connection instance
    """
    # Check if connection already exists in cache
    if name in _CONNECTION_CACHE:
        return _CONNECTION_CACHE[name]

    # Create data directory if it doesn't exist
    DB_DIR.mkdir(parents=True, exist_ok=True)

    # Create a unique database file
    db_filename = f"{name}.sqlite"
    db_path = str(DB_DIR / db_filename)

    # Create connection with optimized settings
    connection = sqlite3.connect(
        db_path,
        timeout=timeout,
        isolation_level=isolation_level,
        detect_types=sqlite3.PARSE_DECLTYPES,
    )

    # Enable foreign keys
    connection.execute("PRAGMA foreign_keys = ON")

    # For better performance
    connection.execute("PRAGMA journal_mode = WAL")

    # Configure connection to return rows as dictionaries
    connection.row_factory = sqlite3.Row

    # Cache connection for reuse
    _CONNECTION_CACHE[name] = connection

    return connection


# Initialize the default connection
qa_connection = get_connection("mcp_qa")


def init_db() -> None:
    """
    Initialize the database schema.

    This creates all tables defined in the schema file.
    """
    # Ensure the database directory exists
    DB_DIR.mkdir(parents=True, exist_ok=True)

    # Execute the schema SQL statements
    execute_schema(qa_connection)


@contextmanager
def get_cursor() -> Generator[sqlite3.Cursor, None, None]:
    """
    Provide a transactional scope around a series of operations.

    Creates a cursor, handles commit/rollback, and ensures proper cleanup.

    Yields:
        Cursor: SQLite cursor

    Example:
        with get_cursor() as cursor:
            cursor.execute("SELECT * FROM source_files")
            rows = cursor.fetchall()
    """
    conn = qa_connection
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()


def dict_factory(cursor: sqlite3.Cursor, row: Tuple) -> Dict[str, Any]:
    """
    Convert a sqlite3.Row to a dictionary.

    Args:
        cursor: SQLite cursor
        row: Database row

    Returns:
        Dict: Dictionary representation of the row
    """
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def format_datetime(dt: Optional[datetime] = None) -> str:
    """
    Format a datetime for storage in SQLite.

    Args:
        dt: Datetime to format, defaults to current UTC time

    Returns:
        str: Formatted datetime string
    """
    if dt is None:
        dt = datetime.utcnow()
    return dt.isoformat()
