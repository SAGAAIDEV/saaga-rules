"""
Utility functions for the MCP suite project.

This module provides utility functions for test path conversion
and other helper methods used throughout the project.
"""

import os
from pathlib import Path
from typing import List, Optional, Set

import tomli

from mcp_qa.logging.logger import logger


def get_git_root():
    """
    Find the git root directory by traversing up from the current file.

    Returns:
        Path: The path to the git root directory.

    Raises:
        FileNotFoundError: If the git root directory cannot be found.
    """

    current_dir = Path(__file__).resolve().parent
    git_root = None

    # Navigate up until we find .git directory
    check_dir = current_dir
    while check_dir != check_dir.parent:
        if (check_dir / ".git").exists():
            git_root = check_dir

            break
        check_dir = check_dir.parent

    if git_root is None:
        error_msg = "Git repository root not found"

        raise FileNotFoundError(error_msg)

    return git_root


def _get_project_names() -> Set[str]:
    """
    Get the project name from pyproject.toml.

    Returns:
        Set of project names defined in pyproject.toml

    Raises:
        ValueError: If no project names can be determined from pyproject.toml
    """
    try:
        git_root = get_git_root()
        pyproject_path = git_root / "pyproject.toml"

        if not pyproject_path.exists():
            logger.warning("pyproject.toml not found at %s", pyproject_path)
            # Default fallback project names
            return {"mcp_qa", "mcp_suite"}

        with open(pyproject_path, "rb") as f:
            pyproject = tomli.load(f)

        # Get project name from pyproject.toml
        project_names = set()
        if "project" in pyproject and "name" in pyproject["project"]:
            project_names.add(pyproject["project"]["name"])

        # Also check dependencies for other potential project names
        if "project" in pyproject and "dependencies" in pyproject["project"]:
            for dep in pyproject["project"]["dependencies"]:
                if dep.startswith("mcp_"):
                    project_names.add(dep.split("[")[0].strip())

        # If no project names found, raise error
        if not project_names:
            msg = "No project names found in pyproject.toml"
            logger.error(msg)
            raise ValueError(msg)

        return project_names
    except ValueError:
        # Re-raise ValueError (from no project names found)
        raise
    except Exception as e:
        # For all other errors, log and use fallback values
        logger.error("Error retrieving project names: %s", e)
        # Return default values if there's an error
        return {"mcp_qa", "mcp_suite"}


def source_to_test_path(source_path: str, test_type: str = "unit") -> str:
    """
    Convert a source file path to its corresponding test file path.

    Args:
        source_path: Path to the source file, relative, starts with src
        test_type: Type of test (unit, integration, etc.)

    Returns:
        Path to the corresponding test file

    Raises:
        ValueError: If the path does not follow the expected format or is invalid

    Examples:
        >>> source_path = "src/mcp_qa/tools/testing/models.py"
        >>> source_to_test_path(source_path)
        'src/tests/unit/tools/testing/test_models.py'
    """
    logger.debug(
        "Converting source path to test path: %s (test_type=%s)", source_path, test_type
    )

    # Validate input
    if not source_path:
        msg = "Source path cannot be empty"
        logger.error(msg)
        raise ValueError(msg)

    # Convert to Path object for better path manipulation
    source_path_obj = Path(os.path.normpath(source_path))
    parts = source_path_obj.parts

    # Find where src is
    try:
        src_index = parts.index("src")
    except ValueError as exc:
        msg = "Path does not contain 'src' directory"
        logger.error("%s: %s", msg, source_path)
        raise ValueError(msg) from exc

    # Extract project name
    if len(parts) <= src_index + 1:
        msg = "Path does not contain a project directory after 'src'"
        logger.error("%s: %s", msg, source_path)
        raise ValueError(msg)

    project_name = parts[src_index + 1]
    valid_project_names = _get_project_names()
    if project_name not in valid_project_names:
        msg = f"Project name '{project_name}' not recognized as a valid project"
        logger.warning("%s: %s. Proceeding anyway.", msg, source_path)

    # Validate file extension for Python files
    if parts[-1].endswith(".py") or parts[-1] == "__init__.py":
        pass  # Valid Python file
    else:
        msg = f"File must be a Python file (.py extension), got '{parts[-1]}'"
        logger.error("%s: %s", msg, source_path)
        raise ValueError(msg)

    # Create the new path parts
    new_parts: List[str] = list(parts[: src_index + 1])  # Keep 'src'
    new_parts.append("tests")  # Add 'tests'
    new_parts.append(test_type)  # Add test type (unit, integration, etc.)

    # Add directories and files (skip project name)
    # Keep the directory structure but prepend test_ only to the filename
    remaining_parts = parts[src_index + 2 :]  # Skip src and project name

    # Add all directories (without test_ prefix)
    if len(remaining_parts) > 1:  # If there are directories besides the filename
        new_parts.extend(
            remaining_parts[:-1]
        )  # Add all except the last part (filename)

    # Handle the filename (last part)
    filename = remaining_parts[-1]
    if filename.endswith(".py"):
        # Add test_ prefix to the filename
        filename_stem = Path(filename).stem  # Get filename without extension
        new_parts.append(f"test_{filename_stem}.py")
    else:
        # It's a directory, just add it as is
        new_parts.append(filename)

    # Create the new path
    test_path = os.path.join(*new_parts)
    logger.debug("Converted source path %s to test path %s", source_path, test_path)

    return test_path


def create_unittest_file(
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
    logger.info("Creating test file for %s (test_type=%s)", source_path, test_type)

    try:
        # Check if source file exists
        if not os.path.isfile(source_path):
            msg = f"Source file does not exist: {source_path}"
            logger.error(msg)
            raise ValueError(msg)

        test_path = source_to_test_path(source_path, test_type)

        # Create directories if needed
        if create_dirs:
            dir_path = os.path.dirname(test_path)
            logger.debug("Creating directories: %s", dir_path)
            os.makedirs(dir_path, exist_ok=True)

        # Skip if file already exists
        if os.path.exists(test_path):
            logger.info("Test file already exists: %s", test_path)
            return test_path

        # Create empty file
        with open(test_path, "w", encoding="utf-8"):
            pass

        logger.info("Created test file: %s", test_path)
        return test_path

    except (ValueError, OSError, IOError) as e:
        logger.error("Error creating test file: %s", e)
        print(f"Error creating test file: {e}")
        return None


def test_to_source_path(test_path: str, test_type: str = "unit") -> str:
    """
    Convert a test file path to its corresponding source file path.

    This is the inverse operation of source_to_test_path.

    Args:
        test_path: Path to the test file
        test_type: Type of test (unit, integration, etc.)

    Returns:
        Path to the corresponding source file

    Raises:
        ValueError: If the path does not follow the expected format or is invalid

    Examples:
        >>> test_path = "src/tests/unit/tools/testing/test_models.py"
        >>> test_to_source_path(test_path)
        'src/mcp_qa/tools/testing/models.py'
    """
    logger.debug(
        "Converting test path to source path: %s (test_type=%s)", test_path, test_type
    )

    # Validate input
    if not test_path:
        msg = "Test path cannot be empty"
        logger.error(msg)
        raise ValueError(msg)

    # Convert to Path object for better path manipulation
    test_path_obj = Path(os.path.normpath(test_path))
    parts = test_path_obj.parts

    # Find where src is
    try:
        src_index = parts.index("src")
    except ValueError as exc:
        msg = "Path does not contain 'src' directory"
        logger.error("%s: %s", msg, test_path)
        raise ValueError(msg) from exc

    # Check if tests directory exists after src
    if src_index + 1 >= len(parts) or parts[src_index + 1] != "tests":
        msg = "Path does not follow expected format src/tests/..."
        logger.error("%s: %s", msg, test_path)
        raise ValueError(msg)

    # Check if test_type directory exists after tests
    if src_index + 2 >= len(parts) or parts[src_index + 2] != test_type:
        msg = f"Path does not contain '{test_type}' directory after 'tests'"
        logger.error("%s: %s", msg, test_path)
        raise ValueError(msg)

    # Validate file extension for Python test files
    filename = parts[-1]
    if not filename.endswith(".py"):
        msg = f"File must be a Python file (.py extension), got '{filename}'"
        logger.error("%s: %s", msg, test_path)
        raise ValueError(msg)

    # Check if filename starts with test_
    if not filename.startswith("test_"):
        msg = f"Test filename must start with 'test_', got '{filename}'"
        logger.error("%s: %s", msg, test_path)
        raise ValueError(msg)

    # Get valid project names
    valid_project_names = _get_project_names()

    # Try to determine project from existence of corresponding source files
    test_type_index = src_index + 2
    module_parts = parts[test_type_index + 1 : -1]  # Directories after test_type
    source_filename = filename[5:]  # Remove test_ prefix

    # Try to find an existing source file with one of the valid project names
    project_name = None
    for name in valid_project_names:
        possible_parts = [
            *parts[: src_index + 1],  # Keep 'src'
            name,  # Add potential project name
            *module_parts,  # Add module directories
            source_filename,  # Add source filename without test_ prefix
        ]
        possible_path = os.path.join(*possible_parts)

        if os.path.exists(possible_path):
            project_name = name
            logger.debug(
                "Found existing source file for project %s: %s", name, possible_path
            )
            break

    # If no existing source file found, use the first project name
    if project_name is None:
        project_name = next(iter(valid_project_names), "mcp_qa")
        logger.debug(
            "No existing source file found, using project name from pyproject.toml: %s",
            project_name,
        )

    # Create the source path parts
    source_parts = [
        *parts[: src_index + 1],  # Keep 'src'
        project_name,  # Add project name
        *module_parts,  # Add module directories
        source_filename,  # Add source filename without test_ prefix
    ]

    # Create the source path
    source_path = os.path.join(*source_parts)
    logger.debug("Converted test path %s to source path %s", test_path, source_path)

    return source_path


def source_to_module_path(source_path: str) -> str:
    """
    Convert a source file path to its module path for coverage reporting.

    Args:
        source_path: Path to the source file

    Returns:
        The module path as a dotted string

    Raises:
        ValueError: If the path does not follow the expected format or is invalid

    Examples:
        >>> source_to_module_path("src/mcp_qa/tools/testing/models.py")
        'mcp_qa.tools.testing.models'
        >>> source_to_module_path("src/mcp_suite/tools/testing/models.py")
        'mcp_suite.tools.testing.models'
        >>> source_to_module_path("src/mcp_qa/tools/testing/__init__.py")
        'mcp_qa.tools.testing'
    """
    logger.debug("Converting source path to module path: %s", source_path)

    # Validate input
    if not source_path:
        msg = "Source path cannot be empty"
        logger.error(msg)
        raise ValueError(msg)

    # Convert to Path object
    source_path_obj = Path(os.path.normpath(source_path))
    parts = source_path_obj.parts

    # Find where src is
    try:
        src_index = parts.index("src")
    except ValueError as exc:
        msg = "Path does not contain 'src' directory"
        logger.error("%s: %s", msg, source_path)
        raise ValueError(msg) from exc

    # Extract project name
    if len(parts) <= src_index + 1:
        msg = "Path does not contain a project directory after 'src'"
        logger.error("%s: %s", msg, source_path)
        raise ValueError(msg)

    # Skip src directory
    module_parts = list(parts[src_index + 1 :])

    # Handle filename
    if module_parts[-1].endswith(".py"):
        # If it's an __init__.py file, exclude it from the module path
        if module_parts[-1] == "__init__.py":
            module_parts = module_parts[:-1]
        else:
            # Remove .py extension from the file
            module_parts[-1] = module_parts[-1][:-3]
    else:
        msg = f"File must be a Python file (.py extension), got '{parts[-1]}'"
        logger.error("%s: %s", msg, source_path)
        raise ValueError(msg)

    # Join with dots to create the module path
    module_path = ".".join(module_parts)
    logger.debug("Converted source path %s to module path %s", source_path, module_path)

    return module_path
