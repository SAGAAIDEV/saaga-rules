"""
Logger configuration for the QA package.

This module provides a simplified logger using PrettyJSONSink to write human-readable
JSON logs to qa.log.
"""

import sqlite3
import sys
import json
import io
from datetime import datetime
from pathlib import Path
from typing import TextIO, List, Dict, Optional

from loguru import logger

# Configure and remove default logger
logger.remove()


def setup_db_logging(db_path=".logs.sqlite3"):
    # Create/connect to SQLite DB
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create logs table if it doesn't exist
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        level TEXT,
        message TEXT,
        function TEXT,
        file TEXT,
        line INTEGER
    )
    """
    )
    conn.commit()

    # Define a function that will process each log and insert it into the database
    def db_sink(message):
        record = message.record
        cursor.execute(
            "INSERT INTO logs (timestamp, level, message, function, file, line) VALUES (?, ?, ?, ?, ?, ?)",
            (
                record["time"].isoformat(),
                record["level"].name,
                record["message"],
                record["function"],
                record["file"].path,
                record["line"],
            ),
        )
        conn.commit()

    # Add the sink to logger
    logger.add(db_sink, level="INFO")

    return conn


async def read_logs(
    n: int = 15, db_path: str = ".logs.sqlite3", level: str = "INFO"
) -> List[Dict]:
    """
    Read the last n log entries from the log database.

    Args:
        n: Number of log entries to read
        db_path: Path to the log database
        level: Filter logs by level (INFO, WARNING, ERROR, etc.)

    Returns:
        List of log entries as dictionaries
    """
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM logs"
        params = []

        if level:
            query += " WHERE level = ?"
            params.append(level)

        query += " ORDER BY id DESC LIMIT ?"
        params.append(n)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Convert rows to dictionaries
        logs = [dict(row) for row in rows]

        conn.close()
        return logs
    except Exception as e:
        logger.error(f"Error reading logs: {str(e)}")
        return []


setup_db_logging()
# Log startup message
logger.info("Logger initialized with Sqlite3")
