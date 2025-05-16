"""
Result processor utilities for pytest.

This module provides functions for processing pytest results and extracting
information about test failures and collection errors.
"""

from typing import Any, Dict, List, Tuple, Optional

from mcp_qa.config import logger as pytest_logger


class PyTestError:
    """Class for pytest errors."""

    def __init__(
        self,
        test_id: str = "",
        filename: str = "",
        line: int = 0,
        message: str = "",
        duration: float = 0.0,
    ):
        """
        Initialize a PyTestError.

        Args:
            test_id: ID of the test (nodeid)
            filename: File containing the test
            line: Line number of the error
            message: Error message
            duration: Test duration
        """
        self.test_id = test_id
        self.filename = filename
        self.line = line
        self.message = message
        self.duration = duration

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PyTestError":
        """
        Create a PyTestError from a dictionary.

        Args:
            data: Dictionary containing test error data

        Returns:
            PyTestError object
        """
        test_id = data.get("nodeid", "")

        # Extract location information if available
        location = data.get("location", {})
        if isinstance(location, dict):
            filename = location.get("file", "")
            line = location.get("line", 0)
        else:
            filename = ""
            line = 0

        # Extract error message from call or longrepr
        message = ""
        if "call" in data and isinstance(data["call"], dict):
            # Try to get the longrepr from the call section
            message = data["call"].get("longrepr", "")
        elif "longrepr" in data:
            # Direct longrepr string
            message = data.get("longrepr", "")

        duration = data.get("duration", 0.0)

        return cls(
            test_id=test_id,
            filename=filename,
            line=line,
            message=message,
            duration=duration,
        )

    def __repr__(self) -> str:
        """String representation."""
        return f"<PyTestError test_id={self.test_id} line={self.line}>"


def process_pytest_data(
    data: Dict[str, Any],
) -> Tuple[Dict[str, Any], List[PyTestError], List]:
    """
    Process pytest results directly from a data dictionary.

    This function processes pytest results and extracts test errors.

    Args:
        data: The pytest results data dictionary

    Returns:
        Tuple[Dict, List[PyTestError], List]: A tuple of
        (summary_data, test_errors, collection_errors)
    """
    pytest_logger.debug("Processing pytest data dictionary")

    # Ensure data is valid
    if not isinstance(data, dict):
        error_msg = "Error: Invalid pytest data format (not a dictionary)"
        pytest_logger.error(error_msg)
        return {"error": error_msg}, [], []

    # Ensure tests key exists
    if "tests" not in data:
        error_msg = "Error: 'tests' key not found in data"
        pytest_logger.error(error_msg)
        return {"error": error_msg}, [], []

    # Extract failed tests
    test_errors = []
    if "tests" in data:
        pytest_logger.debug("Processing test failures")
        for test in data["tests"]:
            if test.get("outcome") == "failed":
                test_error = PyTestError.from_dict(test)
                test_errors.append(test_error)

        if test_errors:
            pytest_logger.warning(f"Found {len(test_errors)} test failures")

    # Extract collection errors
    collection_errors = []
    if "collectors" in data:
        pytest_logger.debug("Processing collection errors")
        for collector in data["collectors"]:
            if collector.get("outcome") == "failed":
                # Just create a list of the raw collector dictionaries for now
                collection_errors.append(collector)

        if collection_errors:
            pytest_logger.warning(f"Found {len(collection_errors)} collection errors")

    # Extract summary information
    summary_data = data.get("summary", {})

    # If summary doesn't exist, create a basic one
    if not summary_data and "tests" in data:
        tests = data["tests"]
        total = len(tests)
        passed = sum(1 for t in tests if t.get("outcome") == "passed")
        failed = sum(1 for t in tests if t.get("outcome") == "failed")
        skipped = sum(1 for t in tests if t.get("outcome") == "skipped")

        summary_data = {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
        }

    pytest_logger.info(f"Test summary: {summary_data}")

    return summary_data, test_errors, collection_errors
