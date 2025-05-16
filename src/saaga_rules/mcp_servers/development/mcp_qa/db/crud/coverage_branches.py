"""
CRUD operations for coverage_branches table.

This module provides CRUD (Create, Read, Update, Delete) operations
for the coverage_branches table in the MCP QA database.
"""

import sqlite3
from typing import Dict, List, Optional, Any

from src.mcp_qa.db.db_manager import get_cursor, format_datetime


def create_coverage_branch(
    coverage_issue_id: int,
    source_line: int,
    end_line: int,
    condition: str,
    branch_type: str,
) -> int:
    """
    Create a new coverage branch record.

    Args:
        coverage_issue_id: ID of the associated coverage issue
        source_line: Line number where the branch starts
        end_line: Line number where the branch ends
        condition: Condition text of the branch
        branch_type: Type of branch

    Returns:
        int: ID of the newly created record
    """
    current_time = format_datetime()

    with get_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO coverage_branches 
            (coverage_issue_id, source_line, end_line, condition, branch_type, created_at) 
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                coverage_issue_id,
                source_line,
                end_line,
                condition,
                branch_type,
                current_time,
            ),
        )
        return cursor.lastrowid


def get_coverage_branch_by_id(branch_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a coverage branch by its ID.

    Args:
        branch_id: ID of the coverage branch

    Returns:
        Dict: Coverage branch data or None if not found
    """
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM coverage_branches WHERE id = ?", (branch_id,))
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None


def get_coverage_branches_by_issue_id(coverage_issue_id: int) -> List[Dict[str, Any]]:
    """
    Get all coverage branches associated with a coverage issue.

    Args:
        coverage_issue_id: ID of the coverage issue

    Returns:
        List[Dict]: List of coverage branch records
    """
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM coverage_branches WHERE coverage_issue_id = ?",
            (coverage_issue_id,),
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def delete_coverage_branch(branch_id: int) -> bool:
    """
    Delete a coverage branch record.

    Args:
        branch_id: ID of the coverage branch to delete

    Returns:
        bool: True if deletion was successful, False otherwise
    """
    with get_cursor() as cursor:
        cursor.execute("DELETE FROM coverage_branches WHERE id = ?", (branch_id,))
        return cursor.rowcount > 0


def delete_coverage_branches_by_issue_id(coverage_issue_id: int) -> int:
    """
    Delete all coverage branches associated with a coverage issue.

    Args:
        coverage_issue_id: ID of the coverage issue

    Returns:
        int: Number of records deleted
    """
    with get_cursor() as cursor:
        cursor.execute(
            "DELETE FROM coverage_branches WHERE coverage_issue_id = ?",
            (coverage_issue_id,),
        )
        return cursor.rowcount


def list_coverage_branches(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    List coverage branches with pagination.

    Args:
        limit: Maximum number of records to return
        offset: Number of records to skip

    Returns:
        List[Dict]: List of coverage branch records
    """
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT * FROM coverage_branches
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
