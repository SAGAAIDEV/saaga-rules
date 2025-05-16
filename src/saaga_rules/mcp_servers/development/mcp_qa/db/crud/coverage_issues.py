"""
CRUD operations for coverage_issues table.

This module provides CRUD (Create, Read, Update, Delete) operations
for the coverage_issues table in the MCP QA database.
"""

import sqlite3
from typing import Dict, List, Optional, Any

from src.mcp_qa.db.db_manager import get_cursor, format_datetime


def create_coverage_issue(
    file_path: str,
    line_number: int,
    source_file_id: Optional[int] = None,
    is_excluded: bool = False,
) -> int:
    """
    Create a new coverage issue record.

    Args:
        file_path: Path to the file with coverage issue
        line_number: Line number with the coverage issue
        source_file_id: ID of the associated source file (optional)
        is_excluded: Whether this issue is excluded from coverage reports

    Returns:
        int: ID of the newly created record
    """
    current_time = format_datetime()

    with get_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO coverage_issues 
            (file_path, line_number, source_file_id, is_excluded, created_at) 
            VALUES (?, ?, ?, ?, ?)
            """,
            (file_path, line_number, source_file_id, is_excluded, current_time),
        )
        return cursor.lastrowid


def get_coverage_issue_by_id(issue_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a coverage issue by its ID.

    Args:
        issue_id: ID of the coverage issue

    Returns:
        Dict: Coverage issue data or None if not found
    """
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM coverage_issues WHERE id = ?", (issue_id,))
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None


def get_coverage_issues_by_file_path(file_path: str) -> List[Dict[str, Any]]:
    """
    Get all coverage issues for a specific file path.

    Args:
        file_path: Path of the file

    Returns:
        List[Dict]: List of coverage issue records
    """
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM coverage_issues WHERE file_path = ?", (file_path,)
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_coverage_issues_by_source_file_id(source_file_id: int) -> List[Dict[str, Any]]:
    """
    Get all coverage issues associated with a source file.

    Args:
        source_file_id: ID of the source file

    Returns:
        List[Dict]: List of coverage issue records
    """
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM coverage_issues WHERE source_file_id = ?", (source_file_id,)
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def update_coverage_issue(
    issue_id: int,
    is_excluded: Optional[bool] = None,
    source_file_id: Optional[int] = None,
) -> bool:
    """
    Update a coverage issue record.

    Args:
        issue_id: ID of the coverage issue to update
        is_excluded: Whether this issue is excluded from coverage reports (optional)
        source_file_id: ID of the associated source file (optional)

    Returns:
        bool: True if update was successful, False otherwise
    """
    update_fields = []
    params = []

    if is_excluded is not None:
        update_fields.append("is_excluded = ?")
        params.append(is_excluded)

    if source_file_id is not None:
        update_fields.append("source_file_id = ?")
        params.append(source_file_id)

    if not update_fields:
        return False

    params.append(issue_id)

    with get_cursor() as cursor:
        cursor.execute(
            f"""
            UPDATE coverage_issues 
            SET {', '.join(update_fields)}
            WHERE id = ?
            """,
            tuple(params),
        )
        return cursor.rowcount > 0


def delete_coverage_issue(issue_id: int) -> bool:
    """
    Delete a coverage issue record.

    Args:
        issue_id: ID of the coverage issue to delete

    Returns:
        bool: True if deletion was successful, False otherwise
    """
    with get_cursor() as cursor:
        cursor.execute("DELETE FROM coverage_issues WHERE id = ?", (issue_id,))
        return cursor.rowcount > 0


def delete_coverage_issues_by_file_path(file_path: str) -> int:
    """
    Delete all coverage issues for a specific file path.

    Args:
        file_path: Path of the file

    Returns:
        int: Number of records deleted
    """
    with get_cursor() as cursor:
        cursor.execute("DELETE FROM coverage_issues WHERE file_path = ?", (file_path,))
        return cursor.rowcount


def delete_coverage_issues_by_source_file_id(source_file_id: int) -> int:
    """
    Delete all coverage issues associated with a source file.

    Args:
        source_file_id: ID of the source file

    Returns:
        int: Number of records deleted
    """
    with get_cursor() as cursor:
        cursor.execute(
            "DELETE FROM coverage_issues WHERE source_file_id = ?", (source_file_id,)
        )
        return cursor.rowcount


def list_coverage_issues(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    List coverage issues with pagination.

    Args:
        limit: Maximum number of records to return
        offset: Number of records to skip

    Returns:
        List[Dict]: List of coverage issue records
    """
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT * FROM coverage_issues
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
