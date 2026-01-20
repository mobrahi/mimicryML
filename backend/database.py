# backend/database.py

import sqlite3
import aiosqlite
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Database path
DB_PATH = Path(__file__).resolve().parent.parent / "database" / "style_transfer.db"
DB_PATH.parent.mkdir(exist_ok=True)

# Initialize database
def init_db():
    """Create database tables if they don't exist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transformations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT UNIQUE NOT NULL,
            session_id TEXT,
            original_filename TEXT NOT NULL,
            original_path TEXT NOT NULL,
            style_name TEXT NOT NULL,
            output_path TEXT,
            status TEXT NOT NULL,
            processing_time FLOAT,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_PATH}")

# Async database operations
class Database:
    
    @staticmethod
    async def create_job(job_id: str, session_id: str, filename: str, 
                         filepath: str, style: str) -> bool:
        """Create a new transformation job"""
        async with aiosqlite.connect(DB_PATH) as db:
            try:
                await db.execute("""
                    INSERT INTO transformations 
                    (job_id, session_id, original_filename, original_path, style_name, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (job_id, session_id, filename, filepath, style, "pending"))
                await db.commit()
                return True
            except Exception as e:
                print(f"Error creating job: {e}")
                return False
    
    @staticmethod
    async def update_job_status(job_id: str, status: str, 
                                output_path: str = None,
                                processing_time: float = None,
                                error_message: str = None) -> bool:
        """Update job status"""
        async with aiosqlite.connect(DB_PATH) as db:
            try:
                if status == "completed":
                    await db.execute("""
                        UPDATE transformations 
                        SET status = ?, output_path = ?, processing_time = ?, 
                            completed_at = CURRENT_TIMESTAMP
                        WHERE job_id = ?
                    """, (status, output_path, processing_time, job_id))
                elif status == "failed":
                    await db.execute("""
                        UPDATE transformations 
                        SET status = ?, error_message = ?, completed_at = CURRENT_TIMESTAMP
                        WHERE job_id = ?
                    """, (status, error_message, job_id))
                else:
                    await db.execute("""
                        UPDATE transformations 
                        SET status = ?
                        WHERE job_id = ?
                    """, (status, job_id))
                
                await db.commit()
                return True
            except Exception as e:
                print(f"Error updating job: {e}")
                return False
    
    @staticmethod
    async def get_job(job_id: str) -> Optional[Dict]:
        """Get job details"""
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM transformations WHERE job_id = ?", (job_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                return None
    
    @staticmethod
    async def get_session_history(session_id: str) -> List[Dict]:
        """Get all transformations for a session"""
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM transformations 
                WHERE session_id = ? 
                ORDER BY created_at DESC
            """, (session_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    @staticmethod
    async def get_all_transformations(limit: int = 50) -> List[Dict]:
        """Get recent transformations (for gallery)"""
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM transformations 
                WHERE status = 'completed'
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

# Initialize database on import
init_db()