"""
CRUD operations for pytest_files table.

This module provides CRUD (Create, Read, Update, Delete) operations
for the pytest_files table in the MCP QA database.
"""

import sqlite3
from typing import Dict, List, Optional, Any

from src.mcp_qa.db.db_manager import get_cursor, format_datetime


def create_pytest_file(
    file_path: str, source_file_id: Optional[int] = None, pytest_summary: str = "{}"
) -> int:
    """
    Create a new pytest file record.

    Args:
        file_path: Path to the pytest file
        source_file_id: ID of the associated source file (optional)
        pytest_summary: JSON summary of pytest results (optional)

    Returns:
        int: ID of the newly created record
    """
    current_time = format_datetime()

    with get_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO pytest_files 
            (file_path, source_file_id, pytest_summary, created_at, updated_at) 
            VALUES (?, ?, ?, ?, ?)
            """,
            (file_path, source_file_id, pytest_summary, current_time, current_time),
        )
        return cursor.lastrowid


def get_pytest_file_by_id(file_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a pytest file by its ID.

    Args:
        file_id: ID of the pytest file

    Returns:
        Dict: Pytest file data or None if not found
    """
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM pytest_files WHERE id = ?", (file_id,))
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None


def get_pytest_file_by_path(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Get a pytest file by its path.

    Args:
        file_path: Path of the pytest file

    Returns:
        Dict: Pytest file data or None if not found
    """
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM pytest_files WHERE file_path = ?", (file_path,))
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None


def get_pytest_files_by_source_id(source_file_id: int) -> List[Dict[str, Any]]:
    """
    Get all pytest files associated with a source file.

    Args:
        source_file_id: ID of the source file

    Returns:
        List[Dict]: List of pytest file records
    """
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM pytest_files WHERE source_file_id = ?", (source_file_id,)
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def update_pytest_file(
    file_id: int,
    source_file_id: Optional[int] = None,
    pytest_summary: Optional[str] = None,
) -> bool:
    """
    Update a pytest file record.

    Args:
        file_id: ID of the pytest file to update
        source_file_id: ID of the associated source file (optional)
        pytest_summary: JSON summary of pytest results (optional)

    Returns:
        bool: True if update was successful, False otherwise
    """
    current_time = format_datetime()
    update_fields = []
    params = []

    if source_file_id is not None:
        update_fields.append("source_file_id = ?")
        params.append(source_file_id)

    if pytest_summary is not None:
        update_fields.append("pytest_summary = ?")
        params.append(pytest_summary)

    update_fields.append("updated_at = ?")
    params.append(current_time)
    params.append(file_id)

    with get_cursor() as cursor:
        cursor.execute(
            f"""
            UPDATE pytest_files 
            SET {', '.join(update_fields)}
            WHERE id = ?
            """,
            tuple(params),
        )
        return cursor.rowcount > 0


def delete_pytest_file(file_id: int) -> bool:
    """
    Delete a pytest file record.

    Args:
        file_id: ID of the pytest file to delete

    Returns:
        bool: True if deletion was successful, False otherwise
    """
    with get_cursor() as cursor:
        cursor.execute("DELETE FROM pytest_files WHERE id = ?", (file_id,))
        return cursor.rowcount > 0


def list_pytest_files(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    List pytest files with pagination.

    Args:
        limit: Maximum number of records to return
        offset: Number of records to skip

    Returns:
        List[Dict]: List of pytest file records
    """
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT * FROM pytest_files
            ORDER BY updated_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
