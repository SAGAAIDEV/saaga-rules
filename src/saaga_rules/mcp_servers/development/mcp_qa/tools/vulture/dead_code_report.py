"""
Dead code detection utility using Vulture.

This module provides a function to generate a JSON report of unused code
in a Python project by running Vulture and processing its output.
"""

import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from mcp_qa.config import logger
from mcp_qa.models.tool_result import ToolResult, ToolStatus
from mcp_qa.utils.decorators import exception_handler


def parse_vulture_line(line: str) -> Optional[Tuple[str, str, int, str, int]]:
    """
    Parse a single line of vulture output.

    Args:
        line: A line of vulture output

    Returns:
        Tuple of (file_path, line_number, issue_description, confidence, line_count) or None
    """
    # Skip empty lines or lines that don't match the expected pattern
    if not line.strip():
        return None

    # Regular expression to match vulture output lines
    pattern = r"(.*):(\d+): (.*) \((\d+)% confidence, (\d+) lines?\)"
    match = re.match(pattern, line)

    if not match:
        logger.warning(f"Could not parse vulture output line: {line}")
        return None

    file_path = match.group(1)
    line_number = int(match.group(2))
    issue_description = match.group(3)
    confidence = int(match.group(4))
    line_count = int(match.group(5))

    return file_path, line_number, issue_description, confidence, line_count


def run_vulture(path: str, min_confidence: int = 60) -> str:
    """
    Run vulture on specified path.

    Args:
        path: Path to the file or directory to analyze
        min_confidence: Minimum confidence threshold (default: 60)

    Returns:
        Vulture output as a string
    """
    cmd = ["vulture", path, f"--min-confidence={min_confidence}", "--sort-by-size"]
    logger.info(f"Running command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)

        if result.returncode not in [0, 3]:  # 0: no issues, 3: dead code found
            logger.error(f"Vulture command failed: {result.stderr}")
            return ""

        return result.stdout
    except Exception as e:
        logger.error(f"Error running vulture: {e}")
        return ""


def process_vulture_output(output: str) -> Dict:
    """
    Process vulture output into a structured format.

    Args:
        output: Raw vulture output

    Returns:
        Dictionary mapping file paths to lists of issues
    """
    result = {}

    for line in output.splitlines():
        parsed = parse_vulture_line(line)
        if not parsed:
            continue

        file_path, line_number, issue_description, confidence, line_count = parsed

        if file_path not in result:
            result[file_path] = []

        result[file_path].append(
            {
                "line": line_number,
                "description": issue_description,
                "confidence": confidence,
                "line_count": line_count,
            }
        )

    return result


@exception_handler()
def generate_dead_code_report(path: str, min_confidence: int = 60) -> ToolResult:
    """
    Generate a report of dead code in a project.

    Args:
        path: Path to the file or directory to analyze
        min_confidence: Minimum confidence threshold (default: 60)

    Returns:
        ToolResult with a report of dead code
    """
    logger.info(f"Generating dead code report for {path}")

    # Make sure the path exists
    if not Path(path).exists():
        return ToolResult(
            status=ToolStatus.ERROR, message=f"Path does not exist: {path}"
        )

    # Run vulture
    output = run_vulture(path, min_confidence)
    if not output:
        return ToolResult(
            status=ToolStatus.SUCCESS,
            message="No dead code found or vulture failed to run.",
        )

    # Process the output
    report = process_vulture_output(output)

    # Calculate statistics
    total_issues = sum(len(issues) for issues in report.values())
    file_count = len(report)

    message = (
        f"Found {total_issues} dead code issues in {file_count} files.\n\n"
        f"Top files by issues:\n"
    )

    # Add top files by number of issues
    sorted_files = sorted(report.items(), key=lambda item: len(item[1]), reverse=True)

    for i, (file_path, issues) in enumerate(sorted_files[:5], 1):
        message += f"{i}. {file_path}: {len(issues)} issues\n"

    # Create a detailed report
    detailed_report = {
        "summary": {"total_issues": total_issues, "file_count": file_count},
        "files": report,
    }

    return ToolResult(status=ToolStatus.SUCCESS, message=message, data=detailed_report)


if __name__ == "__main__":  # pragma: no cover
    import sys

    if len(sys.argv) < 2:
        print(
            "Usage: python -m mcp_qa.tools.vulture.dead_code_report <path> [min_confidence]"
        )
        sys.exit(1)

    path = sys.argv[1]
    min_confidence = int(sys.argv[2]) if len(sys.argv) > 2 else 60

    result = generate_dead_code_report(path, min_confidence)
    print(result.message)

    # Print detailed report if requested
    if "--json" in sys.argv:
        print(json.dumps(result.data, indent=2))
