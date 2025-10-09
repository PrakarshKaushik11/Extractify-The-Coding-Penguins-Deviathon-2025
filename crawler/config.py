"""
Configuration settings for the web crawler.
"""
import os

# Crawler settings
MAX_DEPTH = 3  # Maximum crawl depth
MAX_PAGES = 100  # Maximum number of pages to crawl
REQUEST_TIMEOUT = 10  # Request timeout in seconds
DELAY_BETWEEN_REQUESTS = 1  # Delay between requests in seconds
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# Storage settings
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), 'data')
JSONL_FILE = os.path.join(DATA_DIR, 'crawled_pages.jsonl')
DB_FILE = os.path.join(DATA_DIR, 'pages.db')
LOG_DIR = os.path.join(DATA_DIR, 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'crawl_log.txt')

# NLP settings
SPACY_MODEL = 'en_core_web_sm'  # SpaCy model for NER
MIN_CONFIDENCE = 0.5  # Minimum confidence for entity extraction

# Entity types to extract
ENTITY_TYPES = ['PERSON', 'ORG', 'GPE', 'DATE', 'TITLE', 'DESIGNATION']

# Create necessary directories
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
