"""
Shared utility functions for loading, parsing, and rendering.
"""

import random
import string


def clean_title(text):
    """
    Extract first word from text as title candidate.
    
    Args:
        text: Text value (may be None or numeric)
    
    Returns:
        str or None: First word, or None if empty
    """
    text = str(text).strip() if text is not None else ''
    if not text:
        return None
    return text.split()[0]


def normalize_header(value):
    """
    Normalize column header for comparison.
    
    Args:
        value: Header value
    
    Returns:
        str: Lowercase, whitespace-stripped
    """
    return str(value).strip().lower() if value is not None else ''


def looks_like_number(value):
    """
    Check if a value can be parsed as numeric.
    
    Args:
        value: Value to test
    
    Returns:
        bool: True if numeric
    """
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False


def generate_random_title():
    """
    Generate a random spectrum title code (e.g., 'Spectrum-4821').
    
    Returns:
        str: Random title in format 'Spectrum-XXXX'
    """
    random_code = ''.join(random.choices(string.digits, k=4))
    return f'Spectrum-{random_code}'
