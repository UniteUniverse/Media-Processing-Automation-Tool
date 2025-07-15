import os
import sqlite3
import hashlib
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

class FileRegistry:
    """Manages a database of processed files to prevent duplicates."""
    
    def __init__(self, db_path: str = "processed_files.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database for file tracking."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processed_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_hash TEXT UNIQUE NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                original_name TEXT NOT NULL,
                processed_at TIMESTAMP NOT NULL,
                status TEXT NOT NULL,
                result_path TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_file_hash ON processed_files(file_hash)
        ''')
        
        conn.commit()
        conn.close()
    
    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file content."""
        hash_sha256 = hashlib.sha256()
        
        try:
            with open(file_path, "rb") as f:
                # Read file in chunks to handle large files efficiently
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            raise Exception(f"Error calculating hash for {file_path}: {e}")
    
    def is_already_processed(self, file_path: str) -> Optional[Dict]:
        """Check if file has already been processed based on content hash."""
        file_hash = self.calculate_file_hash(file_path)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM processed_files 
            WHERE file_hash = ? AND status = 'completed'
        ''', (file_hash,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'file_hash': result[1],
                'file_path': result[2],
                'file_size': result[3],
                'original_name': result[4],
                'processed_at': result[5],
                'status': result[6],
                'result_path': result[7]
            }
        return None
    
    def register_file(self, file_path: str, status: str = 'processing', result_path: str = None):
        """Register a file in the database."""
        file_hash = self.calculate_file_hash(file_path)
        file_size = os.path.getsize(file_path)
        original_name = os.path.basename(file_path)
        processed_at = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO processed_files 
            (file_hash, file_path, file_size, original_name, processed_at, status, result_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (file_hash, file_path, file_size, original_name, processed_at, status, result_path))
        
        conn.commit()
        conn.close()
        
        return file_hash
    
    def update_file_status(self, file_hash: str, status: str, result_path: str = None):
        """Update the status of a processed file."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE processed_files 
            SET status = ?, result_path = ?
            WHERE file_hash = ?
        ''', (status, result_path, file_hash))
        
        conn.commit()
        conn.close()
    
    def get_processed_files(self) -> List[Dict]:
        """Get all processed files."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM processed_files ORDER BY processed_at DESC')
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'file_hash': row[1],
                'file_path': row[2],
                'file_size': row[3],
                'original_name': row[4],
                'processed_at': row[5],
                'status': row[6],
                'result_path': row[7]
            }
            for row in results
        ]
    
    def cleanup_orphaned_records(self):
        """Remove records for files that no longer exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT file_hash, file_path FROM processed_files')
        records = cursor.fetchall()
        
        for file_hash, file_path in records:
            if not os.path.exists(file_path):
                cursor.execute('DELETE FROM processed_files WHERE file_hash = ?', (file_hash,))
        
        conn.commit()
        conn.close()
