"""
Repository module for database operations.

This module provides repository functions for database operations
such as saving test results, retrieving test data, and other database
interactions. It abstracts database operations away from the service
layer to maintain a clean separation of concerns.
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union, Any

from loguru import logger

from .db_manager import format_datetime, get_cursor, qa_connection

# Create a logger for the repository module
repo_logger = logger.bind(component="db_repository")

# Type aliases for clarity
SourceFileDict = Dict[str, Any]
PyTestFileDict = Dict[str, Any]
PyTestErrorDict = Dict[str, Any]
CoverageIssueDict = Dict[str, Any]
CoverageBranchDict = Dict[str, Any]

# Constants for error types
ERROR_TYPE_TEST = "PyTestError"


def save_test_results_to_db(
    test_file_path: str,
    summary_data: Dict,
    test_errors: List[PyTestErrorDict],
    collection_errors=None,  # Optional parameter to maintain backward compatibility
) -> None:
    """
    Save test results to the database.

    Args:
        test_file_path: Path to the test file
        summary_data: Summary data from pytest
        test_errors: List of test errors
        collection_errors: This parameter is ignored and only kept for backward compatibility
    """
    repo_logger.info(f"Saving test results to database for {test_file_path}")

    with get_cursor() as cursor:
        # Get or create the PyTestFile record
        cursor.execute(
            "SELECT id FROM pytest_files WHERE file_path = ?", (test_file_path,)
        )
        result = cursor.fetchone()

        if result:
            # If found, get the ID
            test_file_id = result["id"]
            repo_logger.info(f"Found existing PyTestFile record with ID {test_file_id}")
        else:
            # If not found, insert a new record
            repo_logger.info(f"Creating new PyTestFile record for {test_file_path}")
            current_time = format_datetime()

            cursor.execute(
                """
                INSERT INTO pytest_files 
                (file_path, pytest_summary, created_at, updated_at) 
                VALUES (?, ?, ?, ?)
                """,
                (test_file_path, json.dumps(summary_data), current_time, current_time),
            )
            test_file_id = cursor.lastrowid

        # Update the summary data
        cursor.execute(
            "UPDATE pytest_files SET pytest_summary = ?, updated_at = ? WHERE id = ?",
            (json.dumps(summary_data), format_datetime(), test_file_id),
        )

        # Clear existing errors for this test file
        cursor.execute(
            "DELETE FROM pytest_errors WHERE test_file_id = ?", (test_file_id,)
        )

        # Insert new test errors
        for error in test_errors:
            cursor.execute(
                """
                INSERT INTO pytest_errors 
                (node_id, test_file_id, outcome, error_type, result, longrepr, created_at) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    error.get("node_id", ""),
                    test_file_id,
                    error.get("outcome", "failed"),
                    ERROR_TYPE_TEST,
                    json.dumps(error.get("result", [])),
                    error.get("longrepr", ""),
                    format_datetime(),
                ),
            )

        repo_logger.info(f"Test results saved for {test_file_path}")


def save_coverage_issues_to_db(
    source_file_path: str,
    coverage_issues: List[Union[CoverageIssueDict, CoverageBranchDict]],
) -> None:
    """
    Save coverage issues to the database.

    Args:
        source_file_path: Path to the source file
        coverage_issues: List of coverage issues including missing lines and branches
    """
    repo_logger.info(f"Saving coverage issues to database for {source_file_path}")

    with get_cursor() as cursor:
        # Get or create the SourceFile record
        cursor.execute(
            "SELECT id FROM source_files WHERE file_path = ?", (source_file_path,)
        )
        result = cursor.fetchone()

        if result:
            source_file_id = result["id"]
            repo_logger.info(
                f"Found existing SourceFile record with ID {source_file_id}"
            )
        else:
            repo_logger.info(f"Creating new SourceFile record for {source_file_path}")
            current_time = format_datetime()

            cursor.execute(
                """
                INSERT INTO source_files 
                (file_path, file_hash, created_at, updated_at) 
                VALUES (?, ?, ?, ?)
                """,
                (source_file_path, "", current_time, current_time),
            )
            source_file_id = cursor.lastrowid

        # Group issues by type
        line_issues = [
            issue
            for issue in coverage_issues
            if issue.get("type", "") == "CoverageIssue"
        ]
        branch_issues = [
            issue
            for issue in coverage_issues
            if issue.get("type", "") == "CoverageBranch"
        ]

        # Clear existing issues for this source file
        cursor.execute(
            "DELETE FROM coverage_issues WHERE file_path = ?", (source_file_path,)
        )
        # Cascade will delete related branches due to foreign key constraint

        # Add new line issues
        for issue in line_issues:
            cursor.execute(
                """
                INSERT INTO coverage_issues 
                (file_path, source_file_id, line_number, is_excluded, created_at) 
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    source_file_path,
                    source_file_id,
                    issue.get("line_number", 0),
                    bool(issue.get("is_excluded", False)),
                    format_datetime(),
                ),
            )
            coverage_issue_id = cursor.lastrowid

            # If this is also a branch issue, add corresponding branches
            if "branches" in issue and issue["branches"]:
                for branch in issue["branches"]:
                    cursor.execute(
                        """
                        INSERT INTO coverage_branches 
                        (coverage_issue_id, source_line, end_line, condition, branch_type, created_at) 
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            coverage_issue_id,
                            branch.get("source_line", 0),
                            branch.get("end_line", 0),
                            branch.get("condition", ""),
                            branch.get("branch_type", ""),
                            format_datetime(),
                        ),
                    )

        # Add branch issues that weren't part of line issues
        for branch in branch_issues:
            # Only process standalone branches (not already handled through line issues)
            if "parent_issue_id" not in branch:
                cursor.execute(
                    """
                    INSERT INTO coverage_issues 
                    (file_path, source_file_id, line_number, is_excluded, created_at) 
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        source_file_path,
                        source_file_id,
                        branch.get("source_line", 0),
                        False,  # Standalone branches aren't excluded
                        format_datetime(),
                    ),
                )
                coverage_issue_id = cursor.lastrowid

                cursor.execute(
                    """
                    INSERT INTO coverage_branches 
                    (coverage_issue_id, source_line, end_line, condition, branch_type, created_at) 
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        coverage_issue_id,
                        branch.get("source_line", 0),
                        branch.get("end_line", 0),
                        branch.get("condition", ""),
                        branch.get("branch_type", ""),
                        format_datetime(),
                    ),
                )

        # Log the results
        repo_logger.info(
            f"Coverage issues saved for {source_file_path}: "
            f"{len(line_issues)} line issues, {len(branch_issues)} branch issues"
        )


def get_pytest_file(file_path: str) -> Optional[PyTestFileDict]:
    """
    Get a PyTestFile by its file path.

    Args:
        file_path: Path to the test file

    Returns:
        Optional[PyTestFileDict]: The PyTestFile instance if found, None otherwise
    """
    repo_logger.debug(f"Getting PyTestFile for {file_path}")

    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT 
                pf.id, pf.file_path, pf.source_file_id, pf.pytest_summary, 
                pf.created_at, pf.updated_at 
            FROM pytest_files pf
            WHERE pf.file_path = ?
            """,
            (file_path,),
        )
        result = cursor.fetchone()

        if not result:
            repo_logger.debug(f"PyTestFile not found for {file_path}")
            return None

        # Convert row to dictionary
        test_file = dict(result)

        # Get related errors
        cursor.execute(
            """
            SELECT * FROM pytest_errors 
            WHERE test_file_id = ?
            """,
            (test_file["id"],),
        )
        test_errors = [dict(row) for row in cursor.fetchall()]

        # Add errors to test file dictionary
        test_file["test_errors"] = test_errors

        # Parse JSON fields
        if test_file["pytest_summary"]:
            test_file["pytest_summary"] = json.loads(test_file["pytest_summary"])

        return test_file


def get_source_file(file_path: str) -> Optional[SourceFileDict]:
    """
    Get a SourceFile by its file path.

    Args:
        file_path: Path to the source file

    Returns:
        Optional[SourceFileDict]: The SourceFile instance if found, None otherwise
    """
    repo_logger.debug(f"Getting SourceFile for {file_path}")

    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT 
                sf.id, sf.file_path, sf.file_hash, sf.created_at, sf.updated_at 
            FROM source_files sf
            WHERE sf.file_path = ?
            """,
            (file_path,),
        )
        result = cursor.fetchone()

        if not result:
            repo_logger.debug(f"SourceFile not found for {file_path}")
            return None

        # Convert row to dictionary
        source_file = dict(result)

        # Get related coverage issues
        cursor.execute(
            """
            SELECT * FROM coverage_issues 
            WHERE source_file_id = ?
            """,
            (source_file["id"],),
        )
        coverage_issues = []

        for issue_row in cursor.fetchall():
            issue = dict(issue_row)

            # Get related branches for this issue
            cursor.execute(
                """
                SELECT * FROM coverage_branches 
                WHERE coverage_issue_id = ?
                """,
                (issue["id"],),
            )
            branches = [dict(branch_row) for branch_row in cursor.fetchall()]
            issue["branches"] = branches
            coverage_issues.append(issue)

        # Add coverage issues to source file dictionary
        source_file["coverage_issues"] = coverage_issues

        return source_file


def get_next_pytest_error(
    test_file: PyTestFileDict,
) -> Optional[PyTestErrorDict]:
    """
    Get the first PyTestError from the database.

    Args:
        test_file: PyTestFile dictionary to filter errors for

    Returns:
        The first PyTestError object, or None if no errors found
    """
    repo_logger.info(f"get_next_pytest_error called with test_file: {test_file}")
    if test_file:
        repo_logger.info(
            f"Test file details - id: {test_file['id']}, path: {test_file['file_path']}"
        )

    with get_cursor() as cursor:
        test_file_id = test_file["id"]

        # Check for test errors
        cursor.execute(
            """
            SELECT * FROM pytest_errors 
            WHERE test_file_id = ? 
            ORDER BY id LIMIT 1
            """,
            (test_file_id,),
        )
        result = cursor.fetchone()

        if result:
            # Convert row to dictionary
            error = dict(result)
            repo_logger.info(
                f"Found test error: id={error['id']}, node_id={error['node_id']}"
            )

            # Parse JSON fields
            if error.get("result"):
                error["result"] = json.loads(error["result"])

            return error
        else:
            repo_logger.info("No test errors found")

        return None


def delete_pytest_error(node_id: str) -> int:
    """
    Delete all PyTestErrors from the database matching the given node ID.

    Args:
        node_id: The node ID of the PyTestError(s) to delete

    Returns:
        int: The number of errors deleted
    """
    repo_logger.debug(f"Deleting pytest errors with node ID: {node_id}")
    count = 0

    with get_cursor() as cursor:
        # Find and delete regular test errors (using node_id)
        cursor.execute("DELETE FROM pytest_errors WHERE node_id = ?", (node_id,))
        count += cursor.rowcount

        if count == 0:
            repo_logger.debug(f"No pytest errors found with node ID: {node_id}")
            return 0

        cursor.connection.commit()
        repo_logger.info(f"Deleted {count} pytest errors with node ID: {node_id}")
        return count


def get_next_coverage_issue(
    file_path: Optional[str] = None,
) -> Optional[CoverageIssueDict]:
    """
    Get the next coverage issue from the database.

    Args:
        file_path: Optional file path to filter issues for

    Returns:
        Optional[CoverageIssueDict]: The next coverage issue or None if no issues found
    """
    repo_logger.debug(f"Getting next coverage issue for file: {file_path}")

    with get_cursor() as cursor:
        try:
            # Build the query
            query = """
                SELECT * FROM coverage_issues 
                ORDER BY id LIMIT 1
            """
            params = ()

            # Add filter for file_path if provided
            if file_path:
                query = """
                    SELECT * FROM coverage_issues 
                    WHERE file_path = ? 
                    ORDER BY id LIMIT 1
                """
                params = (file_path,)

            # Execute the query
            cursor.execute(query, params)
            result = cursor.fetchone()

            # If we found a coverage issue
            if result:
                # Convert row to dictionary
                issue = dict(result)
                repo_logger.info(
                    f"Found coverage issue: id={issue['id']}, file={issue['file_path']}, line={issue['line_number']}"
                )

                # Get branches for this issue
                cursor.execute(
                    """
                    SELECT * FROM coverage_branches 
                    WHERE coverage_issue_id = ?
                    """,
                    (issue["id"],),
                )
                branches = [dict(row) for row in cursor.fetchall()]
                issue["branches"] = branches

                return issue

            # No coverage issues found
            repo_logger.info("No coverage issues found")
            return None

        except Exception as e:
            repo_logger.error(f"Error getting next coverage issue: {str(e)}")
            return None


def get_next_pytest_error_dict(test_file: Optional[PyTestFileDict] = None) -> dict:
    """
    Get the first PyTestError from the database as a dictionary.

    This function is similar to get_next_pytest_error but returns a dictionary
    representation of the error rather than the SQLModel object, avoiding
    session binding issues.

    Args:
        test_file: Optional PyTestFile dictionary to filter errors for

    Returns:
        Dict: A dictionary representation of the first error or
              {"Success": "No pytest errors were found"} if no errors found
    """
    repo_logger.info(f"get_next_pytest_error_dict called with test_file: {test_file}")

    with get_cursor() as cursor:
        # Build the base query
        test_query = """
            SELECT * FROM pytest_errors 
            ORDER BY id LIMIT 1
        """

        # Add filter if test_file is provided
        params = ()
        if test_file:
            test_file_id = test_file["id"]
            test_query = """
                SELECT * FROM pytest_errors 
                WHERE test_file_id = ? 
                ORDER BY id LIMIT 1
            """
            params = (test_file_id,)

        # Execute the query
        cursor.execute(test_query, params)
        result = cursor.fetchone()

        if result:
            # Convert row to dictionary
            error = dict(result)
            repo_logger.info(
                f"Found test error: id={error['id']}, node_id={error['node_id']}"
            )

            # Parse JSON fields if present
            if error.get("result"):
                try:
                    error["result"] = json.loads(error["result"])
                except json.JSONDecodeError:
                    error["result"] = []

            # Add error type
            error["error_type"] = ERROR_TYPE_TEST

            return error

        repo_logger.info("No pytest errors found")
        return {"Success": "No pytest errors were found"}


def save_source_file_to_db(source_path: str) -> Optional[int]:
    """
    Save a source file to the database.

    Args:
        source_path: Path to the source file

    Returns:
        ID of the created database record or None if failed
    """
    repo_logger.info("Saving source file to database: %s", source_path)

    try:
        with get_cursor() as cursor:
            # Check if the source file is already in the database
            cursor.execute(
                "SELECT id FROM source_files WHERE file_path = ?", (source_path,)
            )
            result = cursor.fetchone()

            # If not, create a new source file record
            if not result:
                repo_logger.debug("Creating source file record: %s", source_path)
                current_time = format_datetime()

                cursor.execute(
                    """
                    INSERT INTO source_files 
                    (file_path, file_hash, created_at, updated_at) 
                    VALUES (?, ?, ?, ?)
                    """,
                    (source_path, "", current_time, current_time),
                )
                source_file_id = cursor.lastrowid
                repo_logger.info(
                    "Source file saved to database with ID: %s", source_file_id
                )
                return source_file_id
            else:
                source_file_id = result["id"]
                repo_logger.info(
                    "Source file already exists in database with ID: %s", source_file_id
                )
                return source_file_id

    except Exception as e:
        repo_logger.error("Error saving source file to database: %s", e)
        import traceback

        repo_logger.error(traceback.format_exc())
        return None


def save_test_file_to_db(test_path: str, source_path: str) -> Optional[int]:
    """
    Save a test file to the database and associate it with a source file.

    Args:
        test_path: Path to the test file
        source_path: Path to the source file

    Returns:
        ID of the created database record or None if failed
    """
    repo_logger.info("Saving test file to database: %s", test_path)

    try:
        # Ensure source file is in the database
        source_file_id = save_source_file_to_db(source_path)
        if source_file_id is None:
            repo_logger.warning("Could not get source file ID for %s", source_path)

        with get_cursor() as cursor:
            # Check if the test file is already in the database
            cursor.execute(
                "SELECT id FROM pytest_files WHERE file_path = ?", (test_path,)
            )
            result = cursor.fetchone()

            # If not, create a new test file record
            if not result:
                repo_logger.debug("Creating test file record: %s", test_path)
                current_time = format_datetime()

                cursor.execute(
                    """
                    INSERT INTO pytest_files 
                    (file_path, source_file_id, pytest_summary, created_at, updated_at) 
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (test_path, source_file_id, "{}", current_time, current_time),
                )
                test_file_id = cursor.lastrowid
                repo_logger.info(
                    "Test file saved to database with ID: %s", test_file_id
                )
                return test_file_id
            else:
                test_file_id = result["id"]
                repo_logger.info(
                    "Test file already exists in database with ID: %s", test_file_id
                )
                return test_file_id

    except Exception as e:
        repo_logger.error("Error saving test file to database: %s", e)
        import traceback

        repo_logger.error(traceback.format_exc())
        return None
