"""
Database logging utilities for pytest results.

This module provides functions for logging pytest results, collection errors,
and test failures to the database. It acts as a bridge between the pytest
runner and the database layer.
"""

import json
import traceback
from typing import Dict, List, Optional, Union

from mcp_qa.config import logger as pytest_logger
from mcp_qa.db.crud.pytest_collection_errors import create_collection_error
from mcp_qa.db.crud.pytest_errors import create_pytest_error
from mcp_qa.db.crud.pytest_files import create_pytest_file, get_pytest_file_by_path


def log_collection_error(
    test_file_path: str,
    error_message: str,
    error_type: str = "collection_error",
    result: Optional[Dict] = None,
) -> Dict[str, Union[int, str, None]]:
    """
    Log a pytest collection error to the database.

    Args:
        test_file_path: Path to the test file
        error_message: Error message
        error_type: Type of error (default: "collection_error")
        result: Additional result data (optional)

    Returns:
        Dict containing status and collection_error_id
    """
    pytest_logger.info(f"Logging collection error for test file: {test_file_path}")

    result_dict = {
        "collection_error_id": None,
        "status": "success",
        "message": "",
    }

    try:
        # Get or create test file record
        test_file = get_pytest_file_by_path(test_file_path)

        if test_file is None:
            pytest_logger.warning(
                f"Test file not found in database, creating: {test_file_path}"
            )
            test_file_id = create_pytest_file(test_file_path)
        else:
            test_file_id = test_file["id"]

        # Convert result to JSON string if provided
        result_json = "[]"
        if result:
            result_json = json.dumps(result)

        # Create collection error record
        collection_error_id = create_collection_error(
            node_id=test_file_path,
            test_file_id=test_file_id,
            outcome="failed",
            error_type=error_type,
            result=result_json,
            longrepr=error_message,
        )

        result_dict["collection_error_id"] = collection_error_id
        result_dict["message"] = "Collection error successfully logged to database"
        return result_dict

    except Exception as e:
        pytest_logger.error(f"Error logging collection error: {str(e)}")
        pytest_logger.error(traceback.format_exc())
        return {
            "collection_error_id": None,
            "status": "error",
            "message": f"Error: {str(e)}",
        }


def log_test_errors(
    test_file_path: str, test_errors: List[dict]
) -> Dict[str, Union[List[int], str, None]]:
    """
    Log test errors to the database.

    Args:
        test_file_path: Path to the test file
        test_errors: List of PyTestError objects

    Returns:
        Dict containing status and list of test error IDs
    """
    pytest_logger.info(
        f"Logging {len(test_errors)} test errors for file: {test_file_path}"
    )

    result_dict = {
        "test_error_ids": [],
        "status": "success",
        "message": "",
    }

    if not test_errors:
        result_dict["message"] = "No test errors to log"
        return result_dict

    try:
        # Get or create test file record
        test_file = get_pytest_file_by_path(test_file_path)

        if test_file is None:
            pytest_logger.warning(
                f"Test file not found in database, creating: {test_file_path}"
            )
            test_file_id = create_pytest_file(test_file_path)
        else:
            test_file_id = test_file["id"]

        # Log each test error
        test_error_ids = []
        for error in test_errors:
            # Create a result dictionary
            result_dict = {
                "filename": error.filename,
                "line": error.line,
                "duration": error.duration,
            }

            # Create test error record
            error_id = create_pytest_error(
                node_id=error.test_id,
                test_file_id=test_file_id,
                outcome="failed",
                error_type="test_failure",
                result=json.dumps(result_dict),
                longrepr=error.message,
            )

            test_error_ids.append(error_id)

        result_dict["test_error_ids"] = test_error_ids
        result_dict["message"] = (
            f"Successfully logged {len(test_error_ids)} test errors"
        )
        return result_dict

    except Exception as e:
        pytest_logger.error(f"Error logging test errors: {str(e)}")
        pytest_logger.error(traceback.format_exc())
        return {
            "test_error_ids": [],
            "status": "error",
            "message": f"Error: {str(e)}",
        }
