"""
CRUD operations for source_files table.

This module provides CRUD (Create, Read, Update, Delete) operations
for the source_files table in the MCP QA database.
"""

import sqlite3
from typing import Dict, List, Optional, Any

from src.mcp_qa.db.db_manager import get_cursor, format_datetime


def create_source_file(file_path: str, file_hash: str = "") -> int:
    """
    Create a new source file record.

    Args:
        file_path: Path to the source file
        file_hash: Hash of the file contents (optional)

    Returns:
        int: ID of the newly created record
    """
    current_time = format_datetime()

    with get_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO source_files 
            (file_path, file_hash, created_at, updated_at) 
            VALUES (?, ?, ?, ?)
            """,
            (file_path, file_hash, current_time, current_time),
        )
        return cursor.lastrowid


def get_source_file_by_id(file_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a source file by its ID.

    Args:
        file_id: ID of the source file

    Returns:
        Dict: Source file data or None if not found
    """
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM source_files WHERE id = ?", (file_id,))
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None


def get_source_file_by_path(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Get a source file by its path.

    Args:
        file_path: Path of the source file

    Returns:
        Dict: Source file data or None if not found
    """
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM source_files WHERE file_path = ?", (file_path,))
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None


def update_source_file(file_id: int, file_hash: Optional[str] = None) -> bool:
    """
    Update a source file record.

    Args:
        file_id: ID of the source file to update
        file_hash: New hash of the file contents (optional)

    Returns:
        bool: True if update was successful, False otherwise
    """
    current_time = format_datetime()
    update_fields = []
    params = []

    if file_hash is not None:
        update_fields.append("file_hash = ?")
        params.append(file_hash)

    update_fields.append("updated_at = ?")
    params.append(current_time)
    params.append(file_id)

    with get_cursor() as cursor:
        cursor.execute(
            f"""
            UPDATE source_files 
            SET {', '.join(update_fields)}
            WHERE id = ?
            """,
            tuple(params),
        )
        return cursor.rowcount > 0


def delete_source_file(file_id: int) -> bool:
    """
    Delete a source file record.

    Args:
        file_id: ID of the source file to delete

    Returns:
        bool: True if deletion was successful, False otherwise
    """
    with get_cursor() as cursor:
        cursor.execute("DELETE FROM source_files WHERE id = ?", (file_id,))
        return cursor.rowcount > 0


def list_source_files(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    List source files with pagination.

    Args:
        limit: Maximum number of records to return
        offset: Number of records to skip

    Returns:
        List[Dict]: List of source file records
    """
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT * FROM source_files
            ORDER BY updated_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
