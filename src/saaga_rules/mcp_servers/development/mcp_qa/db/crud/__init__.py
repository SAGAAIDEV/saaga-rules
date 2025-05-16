"""
CRUD operations for MCP QA database.

This package provides CRUD (Create, Read, Update, Delete) operations
for the database tables used in the MCP QA application.
"""

from .source_files import (
    create_source_file,
    get_source_file_by_id,
    get_source_file_by_path,
    update_source_file,
    delete_source_file,
    list_source_files,
)

from .pytest_files import (
    create_pytest_file,
    get_pytest_file_by_id,
    get_pytest_file_by_path,
    get_pytest_files_by_source_id,
    update_pytest_file,
    delete_pytest_file,
    list_pytest_files,
)

from .pytest_errors import (
    create_pytest_error,
    get_pytest_error_by_id,
    get_pytest_error_by_node_id,
    get_pytest_errors_by_test_file_id,
    delete_pytest_error,
    delete_pytest_errors_by_test_file_id,
    list_pytest_errors,
)

from .pytest_collection_errors import (
    create_collection_error,
    get_collection_error_by_id,
    get_collection_error_by_node_id,
    get_collection_errors_by_test_file_id,
    delete_collection_error,
    delete_collection_errors_by_test_file_id,
    list_collection_errors,
)

from .coverage_issues import (
    create_coverage_issue,
    get_coverage_issue_by_id,
    get_coverage_issues_by_file_path,
    get_coverage_issues_by_source_file_id,
    update_coverage_issue,
    delete_coverage_issue,
    delete_coverage_issues_by_file_path,
    delete_coverage_issues_by_source_file_id,
    list_coverage_issues,
)

from .coverage_branches import (
    create_coverage_branch,
    get_coverage_branch_by_id,
    get_coverage_branches_by_issue_id,
    delete_coverage_branch,
    delete_coverage_branches_by_issue_id,
    list_coverage_branches,
)

__all__ = [
    # Source files
    "create_source_file",
    "get_source_file_by_id",
    "get_source_file_by_path",
    "update_source_file",
    "delete_source_file",
    "list_source_files",
    # Pytest files
    "create_pytest_file",
    "get_pytest_file_by_id",
    "get_pytest_file_by_path",
    "get_pytest_files_by_source_id",
    "update_pytest_file",
    "delete_pytest_file",
    "list_pytest_files",
    # Pytest errors
    "create_pytest_error",
    "get_pytest_error_by_id",
    "get_pytest_error_by_node_id",
    "get_pytest_errors_by_test_file_id",
    "delete_pytest_error",
    "delete_pytest_errors_by_test_file_id",
    "list_pytest_errors",
    # Pytest collection errors
    "create_collection_error",
    "get_collection_error_by_id",
    "get_collection_error_by_node_id",
    "get_collection_errors_by_test_file_id",
    "delete_collection_error",
    "delete_collection_errors_by_test_file_id",
    "list_collection_errors",
    # Coverage issues
    "create_coverage_issue",
    "get_coverage_issue_by_id",
    "get_coverage_issues_by_file_path",
    "get_coverage_issues_by_source_file_id",
    "update_coverage_issue",
    "delete_coverage_issue",
    "delete_coverage_issues_by_file_path",
    "delete_coverage_issues_by_source_file_id",
    "list_coverage_issues",
    # Coverage branches
    "create_coverage_branch",
    "get_coverage_branch_by_id",
    "get_coverage_branches_by_issue_id",
    "delete_coverage_branch",
    "delete_coverage_branches_by_issue_id",
    "list_coverage_branches",
]
