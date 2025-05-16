"""
Configuration package for development servers.
"""

# Import and configure the logger
from pathlib import Path
from mcp_qa.logging.logger import logger

from .constants import ReportPaths


# Logger is automatically configured when imported


__all__ = [
    "ReportPaths",
    "logger",
]
