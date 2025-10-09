"""
Storage handlers for crawled data.
"""
import json
import sqlite3
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class JSONLStorage:
    """Handles storage of crawled pages in JSONL format."""
    
    def __init__(self, filepath):
        self.filepath = filepath
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    def save_page(self, page_data):
        """Save a single page to JSONL file."""
        try:
            with open(self.filepath, 'a', encoding='utf-8') as f:
                json_line = json.dumps(page_data, ensure_ascii=False)
                f.write(json_line + '\n')
            logger.info(f"Saved page to JSONL: {page_data.get('url', 'unknown')}")
        except Exception as e:
            logger.error(f"Error saving to JSONL: {e}")
    
    def read_all(self):
        """Read all pages from JSONL file."""
        pages = []
        try:
            if os.path.exists(self.filepath):
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            pages.append(json.loads(line))
        except Exception as e:
            logger.error(f"Error reading JSONL: {e}")
        return pages


class DatabaseStorage:
    """Handles storage of crawled pages in SQLite database."""
    
    def __init__(self, db_path):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._create_tables()
    
    def _create_tables(self):
        """Create necessary database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                title TEXT,
                content TEXT,
                crawled_at TIMESTAMP,
                depth INTEGER,
                status_code INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_id INTEGER,
                entity_text TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                context TEXT,
                relevant BOOLEAN,
                FOREIGN KEY (page_id) REFERENCES pages (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS structured_entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_id INTEGER,
                entity_category TEXT,
                name TEXT,
                designation TEXT,
                organization TEXT,
                location TEXT,
                context TEXT,
                FOREIGN KEY (page_id) REFERENCES pages (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS page_keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_id INTEGER,
                keyword TEXT,
                FOREIGN KEY (page_id) REFERENCES pages (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database tables created successfully")
    
    def save_page(self, page_data):
        """Save page and associated entities to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO pages (url, title, content, crawled_at, depth, status_code)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                page_data['url'],
                page_data.get('title', ''),
                page_data.get('content', ''),
                page_data.get('crawled_at', datetime.now().isoformat()),
                page_data.get('depth', 0),
                page_data.get('status_code', 200)
            ))
            
            page_id = cursor.lastrowid
            
            if 'entities' in page_data:
                for entity in page_data['entities']:
                    cursor.execute('''
                        INSERT INTO entities (page_id, entity_text, entity_type, context, relevant)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        page_id,
                        entity['text'],
                        entity['label'],
                        entity.get('context', ''),
                        entity.get('relevant', False)
                    ))
            
            if 'structured_data' in page_data:
                structured = page_data['structured_data']
                
                for person in structured.get('persons', []):
                    cursor.execute('''
                        INSERT INTO structured_entities 
                        (page_id, entity_category, name, designation, organization, context)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        page_id,
                        'PERSON',
                        person['name'],
                        person.get('designation'),
                        person.get('organization'),
                        person.get('context', '')
                    ))
                
                for org in structured.get('organizations', []):
                    cursor.execute('''
                        INSERT INTO structured_entities 
                        (page_id, entity_category, name, context)
                        VALUES (?, ?, ?, ?)
                    ''', (page_id, 'ORGANIZATION', org['name'], org.get('context', '')))
                
                for loc in structured.get('locations', []):
                    cursor.execute('''
                        INSERT INTO structured_entities 
                        (page_id, entity_category, name, context)
                        VALUES (?, ?, ?, ?)
                    ''', (page_id, 'LOCATION', loc['name'], loc.get('context', '')))
            
            if 'keywords' in page_data:
                for keyword in page_data['keywords']:
                    cursor.execute('''
                        INSERT INTO page_keywords (page_id, keyword)
                        VALUES (?, ?)
                    ''', (page_id, keyword))
            
            conn.commit()
            logger.info(f"Saved page to database: {page_data['url']}")
            
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def export_to_csv(self, output_file):
        """Export structured entities to CSV."""
        import csv
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT se.entity_category, se.name, se.designation, 
                   se.organization, se.location, se.context, p.url
            FROM structured_entities se
            JOIN pages p ON se.page_id = p.id
        ''')
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Category', 'Name', 'Designation', 'Organization', 'Location', 'Context', 'Source URL'])
            writer.writerows(cursor.fetchall())
        
        conn.close()
        logger.info(f"Exported entities to CSV: {output_file}")
