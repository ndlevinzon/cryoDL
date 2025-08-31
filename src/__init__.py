"""
cryoDL - Python Wrapper for Cryo-EM Deep Learning Software Packages
"""

import os
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Python < 3.11

from .config_manager import ConfigManager
from .cli import CryoDLShell


def _get_version_from_pyproject():
    """Get version from pyproject.toml file."""
    try:
        # Find the pyproject.toml file (go up from src/ to project root)
        project_root = Path(__file__).parent.parent
        pyproject_path = project_root / "pyproject.toml"

        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
                return data["project"]["version"]
    except (KeyError, FileNotFoundError, OSError):
        pass

    # Fallback version
    return "0.3.0"


try:
    import importlib.metadata

    __version__ = importlib.metadata.version("cryodl")
except importlib.metadata.PackageNotFoundError:
    # Fallback to reading from pyproject.toml
    __version__ = _get_version_from_pyproject()

__author__ = "Nathan Levinzon & Shen Lab Team @ The University of Utah"

__all__ = ["ConfigManager", "CryoDLShell"]
