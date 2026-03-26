"""
memory/storage_manager.py — Nexus file index using SQLite.

Saves text notes to disk and indexes them in a database for instant retrieval.
"""

import os
import sys
import sqlite3
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import STORAGE_DIR, DB_PATH


class StorageManager:
    """Manages reading, writing, and searching Nexus stored files."""

    def __init__(self):
        os.makedirs(STORAGE_DIR, exist_ok=True)
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self._conn = sqlite3.connect(DB_PATH)
        self._init_db()

    def _init_db(self):
        """Create the files table if it doesn't exist."""
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL,
                path        TEXT    NOT NULL UNIQUE,
                tags        TEXT,
                created_at  TEXT    NOT NULL
            )
        """)
        self._conn.commit()

    # ─── Save ────────────────────────────────────────────────────────────────

    def save_text(self, name: str, content: str, tags: str = "") -> str:
        """
        Writes a .txt file to STORAGE_DIR and indexes it in the database.

        Args:
            name    : File name (without extension).
            content : Text content to write.
            tags    : Optional comma-separated tags for searching.

        Returns:
            Absolute path to the saved file.
        """
        # Sanitize file name
        safe_name = "".join(c for c in name if c.isalnum() or c in (" ", "_", "-")).strip()
        safe_name = safe_name.replace(" ", "_") or "note"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename  = f"{safe_name}_{timestamp}.txt"
        filepath  = os.path.join(STORAGE_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        # Index in DB
        try:
            self._conn.execute(
                "INSERT INTO files (name, path, tags, created_at) VALUES (?, ?, ?, ?)",
                (safe_name, filepath, tags, datetime.now().isoformat())
            )
            self._conn.commit()
        except sqlite3.IntegrityError:
            # File already indexed (same path), skip
            pass

        return filepath

    # ─── Find ────────────────────────────────────────────────────────────────

    def find_file(self, query: str) -> str | None:
        """
        Search indexed files by name or tags.

        Args:
            query: Search keyword (partial match supported).

        Returns:
            Path to the best matching file, or None if not found.
        """
        query = query.strip().lower()
        cursor = self._conn.execute(
            """
            SELECT path FROM files
            WHERE LOWER(name) LIKE ?
               OR LOWER(tags) LIKE ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (f"%{query}%", f"%{query}%")
        )
        row = cursor.fetchone()
        if row and os.path.exists(row[0]):
            return row[0]
        return None

    # ─── List All ─────────────────────────────────────────────────────────────

    def list_all(self) -> list[dict]:
        """Return all indexed files as a list of dicts."""
        cursor = self._conn.execute(
            "SELECT name, path, tags, created_at FROM files ORDER BY created_at DESC"
        )
        return [
            {"name": r[0], "path": r[1], "tags": r[2], "created_at": r[3]}
            for r in cursor.fetchall()
        ]

    def __del__(self):
        try:
            self._conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    sm = StorageManager()
    path = sm.save_text("test_note", "Hello from Nexus!", tags="test,demo")
    print(f"Saved: {path}")

    found = sm.find_file("test_note")
    print(f"Found: {found}")

    print("\nAll files:")
    for f in sm.list_all():
        print(f"  {f['name']} → {f['path']}")
