"""
Pytest runner utilities.

This module provides functions for running pytest tests and generating reports.
It handles the execution of pytest with coverage and the generation of JSON reports.
"""

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Tuple

from mcp_qa.config import logger


from mcp_qa.tools.testing.utils.file_paths import (
    get_git_root,
    source_to_module_path,
    test_to_source_path,
)

# Create a logger specifically for pytest runner using the standard config logger
pytest_runner_logger = logger.bind(component="pytest_runner")

# Log that the module is being initialized
pytest_runner_logger.info("Pytest runner module initialized")


def run_pytest_with_coverage(
    test_file_path: str,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Run pytest with coverage on a test file and return JSON data.

    Args:
        test_file_path: Path to the test file

    Returns:
        tuple: (pytest_data, coverage_data) - The parsed JSON data from pytest and coverage
    """
    git_root = get_git_root()
    pytest_runner_logger.debug(f"Git root directory: {git_root}")

    try:
        if "::" in test_file_path:
            test_file_path = test_file_path.split("::")[0]
            node_path = test_file_path
        else:
            node_path = test_file_path

        # Convert test file path to source file path and module path
        source_file_path = test_to_source_path(test_file_path)
        module_path = source_to_module_path(source_file_path)

        pytest_runner_logger.debug(f"Test file: {test_file_path}")
        pytest_runner_logger.debug(f"Source file: {source_file_path}")
        pytest_runner_logger.debug(f"Module path: {module_path}")

        # Create human-readable unique filenames for reports
        reports_dir = git_root / "reports"
        os.makedirs(reports_dir, exist_ok=True)

        # Create a unique identifier based on timestamp and test file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_file_hash = hashlib.md5(test_file_path.encode()).hexdigest()[:8]
        test_basename = Path(test_file_path).stem.replace("test_", "")

        # Create the report paths with readable names
        pytest_report_path = (
            reports_dir / f"pytest_{test_basename}_{timestamp}_{test_file_hash}.json"
        )
        coverage_report_path = (
            reports_dir / f"coverage_{test_basename}_{timestamp}_{test_file_hash}.json"
        )

        pytest_runner_logger.debug(
            f"Created report files: pytest={pytest_report_path}, "
            f"coverage={coverage_report_path}"
        )

        # Run pytest with subprocess
        run_pytest_command(
            node_path,
            module_path,
            git_root,
            pytest_report_path,
            coverage_report_path,
        )

        # Load results from files
        pytest_data, coverage_data = load_report_files(
            pytest_report_path, coverage_report_path
        )

        # Add additional context to the result
        # pytest_data["source_file"] = source_file_path
        # pytest_data["module_path"] = module_path

        return pytest_data, coverage_data

    except (ValueError, json.JSONDecodeError) as e:
        pytest_runner_logger.error(
            f"Error in path conversion or JSON parsing: {str(e)}"
        )
        error_data = {
            "error": True,
            "message": f"Error running pytest: {str(e)}",
        }
        return error_data, {}


def run_pytest_command(
    test_file_path: str,
    module_path: str,
    git_root: Path,
    pytest_report_path: str,
    coverage_report_path: str,
) -> subprocess.CompletedProcess:
    """
    Run pytest command with coverage.

    Args:
        test_file_path: Path to the test file
        module_path: Module path for coverage
        git_root: Git root directory
        pytest_report_path: Path to save pytest report
        coverage_report_path: Path to save coverage report

    Returns:
        CompletedProcess: Result of the subprocess run
    """
    # Prepare command to run pytest with coverage and JSON reporting
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        test_file_path,
        "--json-report",
        f"--json-report-file={pytest_report_path}",
        "--cov",
        module_path,
        f"--cov-report=json:{coverage_report_path}",
    ]

    # Log the command being executed
    pytest_runner_logger.info(f"Running command: {' '.join(cmd)}")

    try:
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
        pytest_runner_logger.debug(f"Command stdout: {result.stdout}")
        pytest_runner_logger.debug(f"Command stderr: {result.stderr}")
        pytest_runner_logger.debug(f"Return code: {result.returncode}")

        return result

    except (
        subprocess.SubprocessError,
        FileNotFoundError,
        PermissionError,
        OSError,
    ) as e:
        pytest_runner_logger.error(f"Error running pytest subprocess: {str(e)}")
        raise


def load_report_files(
    pytest_report_path: str, coverage_report_path: str
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
        if not Path(pytest_report_path).exists():
            pytest_runner_logger.error("Pytest report file was not created")
            return {"error": True, "message": "Pytest report file was not created"}, {}

        # Load pytest report
        with open(pytest_report_path, "r", encoding="utf-8") as f:
            pytest_data = json.load(f)

        # Load coverage report if it exists
        coverage_data = {}
        if Path(coverage_report_path).exists():
            with open(coverage_report_path, "r", encoding="utf-8") as f:
                coverage_data = json.load(f)
        else:
            pytest_runner_logger.warning("No coverage data was collected")

        return pytest_data, coverage_data

    finally:
        # Clean up files regardless of success/failure
        # Path(pytest_report_path).unlink(missing_ok=True)
        # Path(coverage_report_path).unlink(missing_ok=True)
        pytest_runner_logger.debug("Report files cleaned up")
