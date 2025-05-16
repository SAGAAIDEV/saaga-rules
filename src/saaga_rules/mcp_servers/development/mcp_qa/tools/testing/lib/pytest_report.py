"""
Utilities for processing pytest JSON report files.

This module provides functions to extract and filter test results from pytest JSON reports,
with a focus on identifying failed tests and collector results.
"""

import json
from typing import Dict, Generator, List, Union


def _yield_nested_results(results: Union[List, Dict]) -> Generator[str, None, None]:
    """
    Recursively yield nested results from pytest collectors.

    Args:
        results: The results dictionary or list to process recursively

    Yields:
        JSON string representations of failed results
    """
    if isinstance(results, list):
        for item in results:
            yield from _yield_nested_results(item)
    elif isinstance(results, dict):
        yield json.dumps(results)
        # Process any nested results if present
        for key in ("result", "results", "children"):
            if key in results and results[key]:
                yield from _yield_nested_results(results[key])


def failed_collector_results(
    pytest_report_data: str,
) -> Generator[str, None, None]:
    """
    Generator that yields only failed results from pytest collectors.

    Args:
        report_path: Path to the pytest JSON report file

    Yields:
        Dict containing the failed test result information
    """

    # Loop through collectors
    for collector in pytest_report_data.get("collectors", []):
        # Check if outcome is 'failed'
        if collector.get("outcome") == "failed":
            # Yield from the results recursively
            yield from _yield_nested_results(collector.get("result", []))


def get_all_failed_tests(
    pytest_report_data: str,
) -> Generator[str, None, None]:
    """
    Generator that yields failed test results from the pytest report.

    Args:
        report_path: Path to the pytest JSON report file

    Yields:
        Dict containing the failed test information
    """

    # Yield all tests with 'failed' outcome
    for test in pytest_report_data.get("tests", []):
        if test.get("outcome") == "failed":
            yield json.dumps(test)
            # Process any nested results if present
            for key in ("result", "results", "children"):
                if key in test and test[key]:
                    yield from _yield_nested_results(test[key])
