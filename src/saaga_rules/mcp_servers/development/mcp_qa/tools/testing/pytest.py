"""
Pytest reporting tool for the SaagaLint MCP server.

This module provides functionality for running pytest tests and generating
comprehensive reports across the entire codebase. It integrates with the MCP
server to provide a unified interface for running tests, analyzing results,
and reporting coverage metrics.

Features:
- Run pytest tests on specified files or across the entire codebase
- Generate detailed JSON reports for test results
- Track and analyze code coverage metrics
- Identify test failures and collection errors
- Store test errors and collection errors in the database
- Provide actionable feedback for resolving test issues
- Generate coverage summaries for the entire codebase
"""

import hashlib
import json
import os
import pathlib
import subprocess
import sys
import traceback
from datetime import datetime
from typing import Any, Dict, Optional, Tuple, Union

from mcp_qa.config import logger as pytest_logger
from mcp_qa.models.tool_result import ToolResult, ToolStatus
from mcp_qa.tools.testing.db_loggers import log_collection_error, log_test_errors
from mcp_qa.tools.testing.files import create_unittest_file
from mcp_qa.tools.testing.lib.process_coverage import process_coverage_json
from mcp_qa.tools.testing.lib.result_processor import process_pytest_data
from mcp_qa.tools.testing.utils.file_paths import (
    get_git_root,
    source_to_module_path,
    test_to_source_path,
)

# Re-export create_unittest_file from files.py to maintain backward compatibility
# This ensures that code importing create_unittest_file from pytest.py will continue to work


async def run_pytest(
    test_file_path: str = "/src",
) -> Union[ToolResult, None]:
    """
    Run pytest tests across the codebase and generate comprehensive reports.

    This function runs pytest from the git root directory to execute tests and
    generate detailed reports on test results and code coverage. It can target
    specific files or the entire codebase, providing insights into test status
    and coverage metrics.

    Args:
        test_file_path: Path to the file or directory to test (relative to git root)
                  Examples:
                  - "src/mcp_suite/base/redis_db/tests/test_redis_manager.py"
                    for a specific test
                  - "src/mcp_suite" for all tests in a module
                  - "." for all tests in the entire codebase

    Returns:
        ToolResult: A ToolResult object containing test results, coverage metrics,
                  and remediation instructions
    """
    try:
        pytest_logger.info(f"Starting pytest run with file_path={test_file_path}")

        # If we have a specific test file, get its corresponding source file
        source_path = None
        module_path = None

        if test_file_path.endswith(".py") and "/tests/" in test_file_path:
            try:
                source_path = test_to_source_path(test_file_path)
                pytest_logger.info(f"Corresponding source file: {source_path}")

                # Convert source path to module path for coverage reporting
                module_path = source_to_module_path(source_path)
                pytest_logger.info(f"Module path for coverage: {module_path}")
            except ValueError as e:
                pytest_logger.warning(
                    f"Could not determine source file: {str(e)}. "
                    "Using default coverage settings."
                )

        # Run pytest and capture results
        pytest_data, coverage_data, cmd_result = run_pytest_with_coverage(
            test_file_path, module_path
        )

        # check for cmd errors, if pytest cmd fails, return an exception

        # process collection errors
        # for each collection error
        # log to the db
        # if there are any collection errors
        # return

        # process pytest errors
        # for each pytest error
        # log to the db
        # return summary of pytest

        # process coverage
        # for each coverage result with missing lines
        # log coverage result to missing file

        # Check for collection errors
        if cmd_result and cmd_result.returncode == 5:  # EXIT_NOTESTSCOLLECTED
            pytest_logger.warning(f"No tests collected for {test_file_path}")
            # Log collection error to database
            error_message = cmd_result.stderr or "No tests collected"
            collection_error_result = log_collection_error(
                test_file_path=test_file_path,
                error_message=error_message,
                error_type="no_tests_collected",
            )

            return ToolResult(
                status=ToolStatus.ERROR,
                message=f"No tests collected for {test_file_path}",
                data={
                    "test_file_path": test_file_path,
                    "source_file_path": source_path,
                    "collection_error": True,
                    "collection_error_id": collection_error_result.get(
                        "collection_error_id"
                    ),
                    "stderr": cmd_result.stderr,
                },
            )

        # Process the pytest data to extract errors and summary
        summary_data, test_errors, _ = process_pytest_data(pytest_data)

        # Log test errors to database
        test_error_result = {}
        if test_errors:
            test_error_result = log_test_errors(
                test_file_path=test_file_path,
                test_errors=test_errors,
            )

        # Process the coverage data to extract issues if available
        coverage_issues = []
        if coverage_data:
            coverage_issues = process_coverage_json(coverage_data)

        return ToolResult(
            status=ToolStatus.SUCCESS,
            message=f"Successfully ran tests for {test_file_path}",
            data={
                "test_file_path": test_file_path,
                "source_file_path": source_path,
                "module_path": module_path,
                "summary": summary_data,
                "errors_count": len(test_errors),
                "test_error_ids": test_error_result.get("test_error_ids", []),
                "coverage_issues_count": len(coverage_issues),
                "json_report_path": pytest_data.get("report_path"),
                "coverage_report_path": coverage_data.get("report_path"),
            },
        )

    except json.JSONDecodeError as e:
        pytest_logger.error(f"JSON parsing error: {str(e)}")
        return ToolResult(
            status=ToolStatus.ERROR,
            message=f"Error parsing JSON: {str(e)}",
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        pytest_logger.error(f"Error in run_pytest: {str(e)}")
        pytest_logger.error(f"Exception traceback: {traceback.format_exc()}")
        return ToolResult(
            status=ToolStatus.EXCEPTION,
            message=f"Error running pytest: {str(e)}",
        )


def run_pytest_with_coverage(
    test_file_path: str,
    module_path: Optional[str] = None,
) -> Tuple[Dict[str, Any], Dict[str, Any], Optional[subprocess.CompletedProcess]]:
    """
    Run pytest with coverage on a test file and return JSON data.

    Args:
        test_file_path: Path to the test file
        module_path: Module path for coverage (optional)

    Returns:
        tuple: (pytest_data, coverage_data, cmd_result) -
               The parsed JSON data from pytest, coverage, and command result
    """
    git_root = get_git_root()
    pytest_logger.debug(f"Git root directory: {git_root}")

    try:
        if "::" in test_file_path:
            test_file_path = test_file_path.split("::")[0]
            node_path = test_file_path
        else:
            node_path = test_file_path

        # Create human-readable unique filenames for reports
        reports_dir = git_root / "reports"
        os.makedirs(reports_dir, exist_ok=True)

        # Create a unique identifier based on timestamp and test file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_file_hash = hashlib.md5(test_file_path.encode()).hexdigest()[:8]
        test_basename = pathlib.Path(test_file_path).stem.replace("test_", "")

        # Create the report paths with readable names
        pytest_report_path = (
            reports_dir / f"pytest_{test_basename}_{timestamp}_{test_file_hash}.json"
        )
        coverage_report_path = (
            reports_dir / f"coverage_{test_basename}_{timestamp}_{test_file_hash}.json"
        )

        pytest_logger.debug(
            f"Created report files: pytest={pytest_report_path}, "
            f"coverage={coverage_report_path}"
        )

        # Prepare command to run pytest with coverage and JSON reporting
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            node_path,
            "--json-report",
            f"--json-report-file={pytest_report_path}",
        ]

        # Add coverage flags if module_path is provided
        if module_path:
            cmd.extend(
                [
                    "--cov",
                    module_path,
                    f"--cov-report=json:{coverage_report_path}",
                ]
            )
        else:
            # Default to full coverage if no specific module is targeted
            cmd.extend(
                [
                    "--cov",
                    f"--cov-report=json:{coverage_report_path}",
                ]
            )

        # Log the command being executed
        pytest_logger.info(f"Running command: {' '.join(cmd)}")

        # Run pytest with subprocess
        result = subprocess.run(
            cmd,
            cwd=git_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

        # Log the command output
        pytest_logger.debug(f"Command stdout: {result.stdout}")
        pytest_logger.debug(f"Command stderr: {result.stderr}")
        pytest_logger.debug(f"Return code: {result.returncode}")

        # Load results from files
        pytest_data, coverage_data = load_report_files(
            pytest_report_path, coverage_report_path
        )

        # Add report paths to the data dictionaries
        pytest_data["report_path"] = str(pytest_report_path)
        coverage_data["report_path"] = str(coverage_report_path)

        return pytest_data, coverage_data, result

    except (ValueError, json.JSONDecodeError) as e:
        pytest_logger.error(f"Error in path conversion or JSON parsing: {str(e)}")
        error_data = {
            "error": True,
            "message": f"Error running pytest: {str(e)}",
        }
        return error_data, {}, None


def load_report_files(
    pytest_report_path: Union[str, pathlib.Path],
    coverage_report_path: Union[str, pathlib.Path],
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Load and parse the pytest and coverage report files.

    Args:
        pytest_report_path: Path to the pytest report file
        coverage_report_path: Path to the coverage report file

    Returns:
        tuple: (pytest_data, coverage_data) - The parsed JSON data

    Raises:
        JSONDecodeError: If the report files cannot be parsed
        OSError: If the report files cannot be read
    """
    try:
        # Check if report files were created
        if not pathlib.Path(pytest_report_path).exists():
            pytest_logger.error("Pytest report file was not created")
            return {"error": True, "message": "Pytest report file was not created"}, {}

        # Load pytest report
        with open(pytest_report_path, "r", encoding="utf-8") as f:
            pytest_data = json.load(f)

        # Load coverage report if it exists
        coverage_data = {}
        if pathlib.Path(coverage_report_path).exists():
            with open(coverage_report_path, "r", encoding="utf-8") as f:
                coverage_data = json.load(f)
        else:
            pytest_logger.warning("No coverage data was collected")

        return pytest_data, coverage_data

    except Exception as e:
        pytest_logger.error(f"Error loading report files: {str(e)}")
        pytest_logger.error(traceback.format_exc())
        return {"error": True, "message": f"Error: {str(e)}"}, {}


async def next_pytest_error(test_file_path: str) -> Dict:
    """
    Get the next pytest error.

    This function would normally retrieve the first pytest error from the database,
    but since database functionality has been removed, it returns a stub response.

    Args:
        test_file_path: Path to the test file to filter errors by

    Returns:
        Dict: A dictionary with a message indicating the database functionality is disabled
    """
    pytest_logger.info(f"Getting next pytest error for {test_file_path}")

    return {
        "status": "database_disabled",
        "message": "Database functionality has been disabled in this version.",
    }


async def delete_pytest_error(node_id: str) -> Dict:
    """
    Delete a pytest error.

    This function would normally remove pytest errors with the specified node ID from the database,
    but since database functionality has been removed, it returns a stub response.

    Args:
        node_id: The node ID of the pytest error to delete

    Returns:
        Dict: A dictionary with a message indicating the database functionality is disabled
    """
    pytest_logger.info(f"Deleting pytest error with node ID: {node_id}")

    return {
        "status": "database_disabled",
        "message": "Database functionality has been disabled in this version.",
    }
