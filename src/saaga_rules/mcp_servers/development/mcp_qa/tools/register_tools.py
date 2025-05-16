"""
Tool registration for the SaagaLint MCP server.

This module provides a function to register all tools with the MCP server.
Each tool is imported from its respective module and registered with the
MCP server using the tool() decorator.

Available tools:
- run_pytest: Run pytest tests and analyze results
- run_coverage: Check code coverage and identify untested code
- run_autoflake: Detect and fix unused imports and variables
- run_flake8: Check code style and quality using flake8
"""

from mcp.server.fastmcp import FastMCP
from mcp_qa.logging.logger import read_logs


from mcp_qa.tools.formatter.formatter_tool import formatter
from mcp_qa.tools.linter.flake8_report import flake8_report
from mcp_qa.tools.linter.pylint_tool import pylint_report

from mcp_qa.tools.testing.pytest import (
    run_pytest,
    create_unittest_file,
    next_pytest_error,
    delete_pytest_error,
)
from mcp_qa.tools.testing.utils.file_paths import (
    source_to_test_path as get_testfile,
)

# Remove logger imports and initialization
# from mcp_suite.servers.qa import logger
# Bind the component field to the logger
# logger = logger.bind(component="tools")


def register_tools(mcp: FastMCP) -> None:
    """
    Register all tools with the MCP server.

    This function registers each tool with the MCP server using the tool()
    decorator. Each tool is imported from its respective module and registered
    with the MCP server.

    Args:
        mcp: The MCP server instance
    """
    # Register logging tools
    mcp.tool()(read_logs)
    # Register formatter tool
    mcp.tool()(formatter)

    # Run flake8 report
    mcp.tool()(flake8_report)

    # pytests
    mcp.tool()(create_unittest_file)
    mcp.tool()(get_testfile)
    mcp.tool()(run_pytest)
    mcp.tool()(next_pytest_error)
    mcp.tool()(delete_pytest_error)

    # coverage

    # Register pylint tool
    mcp.tool()(pylint_report)

    # get pylint issue

    # mcp.tool()(clear_logs)
