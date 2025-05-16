"""
CRUD operations for pytest_errors table.

This module provides CRUD (Create, Read, Update, Delete) operations
for the pytest_errors table in the MCP QA database.
"""

import sqlite3
from typing import Dict, List, Optional, Any

from src.mcp_qa.db.db_manager import get_cursor, format_datetime


def create_pytest_error(
    node_id: str,
    test_file_id: int,
    outcome: str,
    error_type: str,
    result: str = "[]",
    longrepr: str = "",
) -> int:
    """
    Create a new pytest error record.

    Args:
        node_id: Node ID of the test
        test_file_id: ID of the associated test file
        outcome: Test outcome (e.g., "failed", "skipped")
        error_type: Type of error
        result: JSON array with test result details (optional)
        longrepr: Long representation of the error (optional)

    Returns:
        int: ID of the newly created record
    """
    current_time = format_datetime()

    with get_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO pytest_errors 
            (node_id, test_file_id, outcome, error_type, result, longrepr, created_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                node_id,
                test_file_id,
                outcome,
                error_type,
                result,
                longrepr,
                current_time,
            ),
        )
        return cursor.lastrowid


def get_pytest_error_by_id(error_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a pytest error by its ID.

    Args:
        error_id: ID of the pytest error

    Returns:
        Dict: Pytest error data or None if not found
    """
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM pytest_errors WHERE id = ?", (error_id,))
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None


def get_pytest_error_by_node_id(node_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a pytest error by its node ID.

    Args:
        node_id: Node ID of the test

    Returns:
        Dict: Pytest error data or None if not found
    """
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM pytest_errors WHERE node_id = ?", (node_id,))
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None


def get_pytest_errors_by_test_file_id(test_file_id: int) -> List[Dict[str, Any]]:
    """
    Get all pytest errors associated with a test file.

    Args:
        test_file_id: ID of the test file

    Returns:
        List[Dict]: List of pytest error records
    """
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM pytest_errors WHERE test_file_id = ?", (test_file_id,)
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def delete_pytest_error(error_id: int) -> bool:
    """
    Delete a pytest error record.

    Args:
        error_id: ID of the pytest error to delete

    Returns:
        bool: True if deletion was successful, False otherwise
    """
    with get_cursor() as cursor:
        cursor.execute("DELETE FROM pytest_errors WHERE id = ?", (error_id,))
        return cursor.rowcount > 0


def delete_pytest_errors_by_test_file_id(test_file_id: int) -> int:
    """
    Delete all pytest errors associated with a test file.

    Args:
        test_file_id: ID of the test file

    Returns:
        int: Number of records deleted
    """
    with get_cursor() as cursor:
        cursor.execute(
            "DELETE FROM pytest_errors WHERE test_file_id = ?", (test_file_id,)
        )
        return cursor.rowcount


def list_pytest_errors(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    List pytest errors with pagination.

    Args:
        limit: Maximum number of records to return
        offset: Number of records to skip

    Returns:
        List[Dict]: List of pytest error records
    """
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT * FROM pytest_errors
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
