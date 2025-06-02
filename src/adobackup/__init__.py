"""
Azure DevOps Backup Tool (adobackup) - Core Package
"""

__version__ = "1.0.0"
__all__ = ['cli', 'core', 'modules']  # Explicitly expose submodules

# Optional: Initialize package-level logging
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())