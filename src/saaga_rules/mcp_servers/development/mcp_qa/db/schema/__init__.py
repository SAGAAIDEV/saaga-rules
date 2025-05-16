"""
Schema module for MCP QA database.

This module provides functionality for loading and executing the SQL schema
for the MCP QA database.
"""

import pathlib
import sqlite3
from typing import List


def get_schema_path() -> pathlib.Path:
    """
    Get the path to the schema file.

    Returns:
        Path to the schema.sql file
    """
    return pathlib.Path(__file__).parent / "schema.sql"


def load_schema() -> str:
    """
    Load the schema file contents.

    Returns:
        str: Contents of the schema.sql file
    """
    schema_path = get_schema_path()
    return schema_path.read_text()


def get_schema_statements() -> List[str]:
    """
    Get the SQL statements from the schema file.

    Returns:
        List[str]: List of SQL statements
    """
    schema = load_schema()
    # Split on semicolons but exclude empty statements
    statements = [stmt.strip() for stmt in schema.split(";") if stmt.strip()]
    return statements


def execute_schema(conn: sqlite3.Connection) -> None:
    """
    Execute the schema statements on a database connection.

    Args:
        conn: SQLite connection
    """
    cursor = conn.cursor()
    statements = get_schema_statements()

    for statement in statements:
        cursor.execute(statement)

    conn.commit()
