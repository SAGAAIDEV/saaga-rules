"""
Tools for creating and managing test files and their structure.

This module provides utilities for working with the file structure of tests
in the MCP QA codebase. It includes functionality to:

1. Create unittest files in the correct locations based on source files
2. Navigate between test files and their corresponding source files
3. Maintain proper directory structure for tests
4. Save file relationships to the database for tracking

The module ensures that test files follow project conventions and are
properly organized in the codebase, with corresponding entries in the database
to maintain the relationships between test files and their source files.
"""

import json
import pathlib
import traceback
from typing import Dict, Optional, Union

from mcp_qa.config import logger as pytest_logger
from mcp_qa.tools.testing.utils.file_paths import (
    source_to_test_path,
    test_to_source_path,
)
from mcp_qa.db import save_source_file_to_db, save_test_file_to_db


async def async_source_to_test_path(source_path: str, test_type: str = "unit") -> str:
    """
    Async wrapper for converting a source file path to its corresponding test file path.

    Args:
        source_path: Path to the source file
        test_type: Type of test (unit, integration, etc.)

    Returns:
        Path to the corresponding test file

    Raises:
        ValueError: If the path does not follow the expected format or is invalid
    """
    pytest_logger.debug(
        "Converting source path to test path (async): %s (test_type=%s)",
        source_path,
        test_type,
    )
    return source_to_test_path(source_path, test_type)


async def async_test_to_source_path(test_path: str, test_type: str = "unit") -> str:
    """
    Async wrapper for converting a test file path to its corresponding source file path.

    Args:
        test_path: Path to the test file
        test_type: Type of test (unit, integration, etc.)

    Returns:
        Path to the corresponding source file

    Raises:
        ValueError: If the path does not follow the expected format or is invalid
    """
    pytest_logger.debug(
        "Converting test path to source path (async): %s (test_type=%s)",
        test_path,
        test_type,
    )
    return test_to_source_path(test_path, test_type)


async def save_files_to_db(
    test_path: str, source_path: str
) -> Dict[str, Union[str, int, None]]:
    """
    Save both test and source files to the database asynchronously.

    Args:
        test_path: Path to the test file
        source_path: Path to the source file

    Returns:
        Dict containing source_file_id and test_file_id
    """
    pytest_logger.info(
        "Saving files to database (async) - source: %s, test: %s",
        source_path,
        test_path,
    )

    result = {
        "source_file_id": None,
        "test_file_id": None,
        "status": "success",
        "message": "",
    }

    try:
        # Save source file first
        source_file_id = save_source_file_to_db(source_path)
        result["source_file_id"] = source_file_id

        if source_file_id is None:
            result["status"] = "warning"
            result["message"] += "Failed to save source file to database. "

        # Save test file
        test_file_id = save_test_file_to_db(test_path, source_path)
        result["test_file_id"] = test_file_id

        if test_file_id is None:
            result["status"] = "warning"
            result["message"] += "Failed to save test file to database. "

        if result["status"] == "success":
            result["message"] = "Both files successfully saved to database."

        return result

    except Exception as e:
        pytest_logger.error("Error saving files to database: %s", e)
        pytest_logger.error(traceback.format_exc())
        return {
            "source_file_id": None,
            "test_file_id": None,
            "status": "error",
            "message": f"Error: {str(e)}",
        }


async def create_unittest_file(
    source_path: str,
    test_type: str = "unit",
    create_dirs: bool = True,
) -> Optional[str]:
    """
    Create a test file for the given source file.

    Args:
        source_path: Path to the source file
        test_type: Type of test (unit, integration, etc.)
        create_dirs: Whether to create directories

    Returns:
        Path to the created test file or None if failed

    Raises:
        ValueError: If the source path is invalid
        OSError: If there are filesystem-related errors
    """
    pytest_logger.info(
        "Creating test file for %s (test_type=%s)", source_path, test_type
    )

    try:
        # Check if source file exists
        source_file = pathlib.Path(source_path)
        if not source_file.is_file():
            msg = f"Source file does not exist: {source_path}"
            pytest_logger.error(msg)
            raise ValueError(msg)

        # Save the source file to the database first
        source_file_id = save_source_file_to_db(source_path)
        if source_file_id is None:
            pytest_logger.warning(
                "Failed to save source file to database: %s", source_path
            )

        test_path = source_to_test_path(source_path, test_type)
        test_file = pathlib.Path(test_path)

        # Create directories if needed
        if create_dirs:
            dir_path = test_file.parent
            pytest_logger.debug("Creating directories: %s", str(dir_path))
            dir_path.mkdir(parents=True, exist_ok=True)

        # Skip if file already exists
        if test_file.exists():
            pytest_logger.info("Test file already exists: %s", test_path)
            # If file exists but not in DB, add it to DB
            save_test_file_to_db(test_path, source_path)
            return test_path

        # Create empty file
        test_file.touch()

        # Save the test file to the database
        save_test_file_to_db(test_path, source_path)

        pytest_logger.info("Created test file: %s", test_path)
        return test_path

    except (ValueError, OSError, IOError) as e:
        pytest_logger.error("Error creating test file: %s", e)
        print(f"Error creating test file: {e}")
        return None
