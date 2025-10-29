"""
Helper utilities and functions.
"""
from typing import List, Optional
from pathlib import Path


def validate_file_exists(file_path: str) -> bool:
    """
    Validate that a file exists.
    
    Args:
        file_path: Path to file
        
    Returns:
        bool: True if file exists
    """
    return Path(file_path).exists()


def get_markdown_files(directory: str) -> List[Path]:
    """
    Get all markdown files in a directory.
    
    Args:
        directory: Directory path
        
    Returns:
        List[Path]: List of markdown file paths
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        return []
    
    return sorted(dir_path.glob("*.md"))


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        str: Truncated string
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_error_message(error: Exception, context: Optional[str] = None) -> str:
    """
    Format an error message with optional context.
    
    Args:
        error: Exception object
        context: Optional context string
        
    Returns:
        str: Formatted error message
    """
    error_msg = str(error)
    if context:
        return f"{context}: {error_msg}"
    return error_msg
