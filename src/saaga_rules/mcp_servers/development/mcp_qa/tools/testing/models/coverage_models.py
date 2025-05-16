"""
Coverage models for storing code coverage results.

This module provides simple stub classes for coverage analysis data
since the actual models have been removed.
"""


# Define stub classes instead of importing from removed models
class BranchCoverage:
    """Stub class for branch coverage information."""

    def __init__(self, file_path="", line_number=0, branch_number=0, is_covered=False):
        self.file_path = file_path
        self.line_number = line_number
        self.branch_number = branch_number
        self.is_covered = is_covered

    def __repr__(self) -> str:
        return f"<BranchCoverage file={self.file_path} line={self.line_number} branch={self.branch_number} covered={self.is_covered}>"


class CoverageIssue:
    """Stub class for coverage issues."""

    def __init__(
        self, file_path="", start_line=0, end_line=0, issue_type="", description=""
    ):
        self.file_path = file_path
        self.start_line = start_line
        self.end_line = end_line
        self.issue_type = issue_type
        self.description = description

    def __repr__(self) -> str:
        return f"<CoverageIssue file={self.file_path} lines={self.start_line}-{self.end_line} type={self.issue_type}>"


__all__ = ["BranchCoverage", "CoverageIssue"]
