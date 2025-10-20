# api/validators.py
"""
Input validation utilities for API endpoints.
"""
import re
from typing import List
from urllib.parse import urlparse


class ValidationError(Exception):
    """Custom validation error."""
    pass


def validate_url(url: str) -> str:
    """
    Validate and normalize a URL.
    
    Args:
        url: URL string to validate
        
    Returns:
        Normalized URL string
        
    Raises:
        ValidationError: If URL is invalid
    """
    if not url or not isinstance(url, str):
        raise ValidationError("URL must be a non-empty string")
    
    url = url.strip()
    
    # Add scheme if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            raise ValidationError(f"Invalid URL format: {url}")
        if parsed.scheme not in ('http', 'https'):
            raise ValidationError(f"Only HTTP/HTTPS URLs are supported: {url}")
        return url
    except Exception as e:
        raise ValidationError(f"Invalid URL: {e}")


def validate_keywords(keywords: List[str], max_keywords: int = 50) -> List[str]:
    """
    Validate and sanitize keywords list.
    
    Args:
        keywords: List of keyword strings
        max_keywords: Maximum number of keywords allowed
        
    Returns:
        Sanitized list of keywords
        
    Raises:
        ValidationError: If keywords are invalid
    """
    if not isinstance(keywords, list):
        raise ValidationError("Keywords must be a list")
    
    if len(keywords) > max_keywords:
        raise ValidationError(f"Too many keywords. Maximum allowed: {max_keywords}")
    
    sanitized = []
    for kw in keywords:
        if not isinstance(kw, str):
            continue
        
        # Remove excessive whitespace and sanitize
        kw = ' '.join(kw.strip().split())
        
        # Skip empty or too long keywords
        if not kw or len(kw) > 100:
            continue
        
        # Skip keywords with suspicious patterns (SQL injection, XSS attempts)
        if re.search(r'[<>{}()\[\]\'\"\\;]', kw):
            continue
        
        sanitized.append(kw)
    
    return sanitized


def validate_max_pages(max_pages: int, min_val: int = 1, max_val: int = 1000) -> int:
    """
    Validate max_pages parameter.
    
    Args:
        max_pages: Maximum number of pages to crawl
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        Validated max_pages value
        
    Raises:
        ValidationError: If value is out of range
    """
    if not isinstance(max_pages, int):
        raise ValidationError("max_pages must be an integer")
    
    if max_pages < min_val:
        raise ValidationError(f"max_pages must be at least {min_val}")
    
    if max_pages > max_val:
        raise ValidationError(f"max_pages cannot exceed {max_val}")
    
    return max_pages


def validate_max_depth(max_depth: int, min_val: int = 0, max_val: int = 10) -> int:
    """
    Validate max_depth parameter.
    
    Args:
        max_depth: Maximum crawl depth
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        Validated max_depth value
        
    Raises:
        ValidationError: If value is out of range
    """
    if not isinstance(max_depth, int):
        raise ValidationError("max_depth must be an integer")
    
    if max_depth < min_val:
        raise ValidationError(f"max_depth must be at least {min_val}")
    
    if max_depth > max_val:
        raise ValidationError(f"max_depth cannot exceed {max_val}")
    
    return max_depth


def validate_min_score(min_score: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """
    Validate min_score parameter.
    
    Args:
        min_score: Minimum confidence score
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        Validated min_score value
        
    Raises:
        ValidationError: If value is out of range
    """
    if not isinstance(min_score, (int, float)):
        raise ValidationError("min_score must be a number")
    
    min_score = float(min_score)
    
    if min_score < min_val:
        raise ValidationError(f"min_score must be at least {min_val}")
    
    if min_score > max_val:
        raise ValidationError(f"min_score cannot exceed {max_val}")
    
    return min_score
