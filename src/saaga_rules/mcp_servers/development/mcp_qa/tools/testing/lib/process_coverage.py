"""
Coverage data processing utilities.

This module provides functions for processing coverage data from pytest-cov
and identifying missing coverage areas.
"""

from typing import Any, Dict, List

from mcp_qa.config import logger as coverage_logger


def process_coverage_json(coverage_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Process coverage data and extract issues.

    Args:
        coverage_data: The coverage data dictionary from pytest-cov

    Returns:
        List of coverage issues (files with missing lines)
    """
    coverage_logger.debug("Processing coverage data")

    coverage_issues = []

    if not coverage_data or not isinstance(coverage_data, dict):
        coverage_logger.warning("Invalid coverage data format")
        return []

    # Extract files data if available
    files_data = coverage_data.get("files", {})
    if not files_data:
        coverage_logger.warning("No files data found in coverage report")
        return []

    for file_path, file_data in files_data.items():
        # Skip if no file data
        if not file_data or not isinstance(file_data, dict):
            continue

        # Extract missing lines
        missing_lines = file_data.get("missing_lines", [])

        # Skip if no missing lines
        if not missing_lines:
            continue

        # Extract line numbers covered and missed
        line_rate = file_data.get("summary", {}).get("percent_covered", 0)

        # Create coverage issue record
        coverage_issue = {
            "file_path": file_path,
            "missing_lines": missing_lines,
            "line_rate": line_rate,
            "num_missing": len(missing_lines),
        }

        coverage_issues.append(coverage_issue)

    if coverage_issues:
        coverage_logger.info(f"Found {len(coverage_issues)} files with coverage issues")

    return coverage_issues
