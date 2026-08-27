import sqlite3
from pathlib import Path
from datetime import datetime, timezone


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "research_papers.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_database():
    connection = get_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS papers (
            paper_id TEXT PRIMARY KEY,
            original_filename TEXT NOT NULL,
            saved_filename TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            file_hash TEXT NOT NULL UNIQUE,
            uploaded_at TEXT NOT NULL,
            chunks INTEGER DEFAULT 0
        )
        """
    )

    connection.commit()
    connection.close()


def add_paper(
    paper_id,
    original_filename,
    saved_filename,
    file_size,
    file_hash,
    chunks=0
):
    connection = get_connection()

    connection.execute(
        """
        INSERT INTO papers (
            paper_id,
            original_filename,
            saved_filename,
            file_size,
            file_hash,
            uploaded_at,
            chunks
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            paper_id,
            original_filename,
            saved_filename,
            file_size,
            file_hash,
            datetime.now(timezone.utc).isoformat(),
            chunks
        )
    )

    connection.commit()
    connection.close()


def get_paper_by_hash(file_hash):
    connection = get_connection()

    paper = connection.execute(
        """
        SELECT *
        FROM papers
        WHERE file_hash = ?
        """,
        (file_hash,)
    ).fetchone()

    connection.close()

    return dict(paper) if paper else None


def get_all_papers():
    connection = get_connection()

    papers = connection.execute(
        """
        SELECT *
        FROM papers
        ORDER BY uploaded_at DESC
        """
    ).fetchall()

    connection.close()

    return [dict(paper) for paper in papers]


def get_paper(paper_id):
    connection = get_connection()

    paper = connection.execute(
        """
        SELECT *
        FROM papers
        WHERE paper_id = ?
        """,
        (paper_id,)
    ).fetchone()

    connection.close()

    return dict(paper) if paper else None


def update_paper_chunks(paper_id, chunks):
    connection = get_connection()

    connection.execute(
        """
        UPDATE papers
        SET chunks = ?
        WHERE paper_id = ?
        """,
        (chunks, paper_id)
    )

    connection.commit()
    connection.close()


def delete_paper(paper_id):
    connection = get_connection()

    cursor = connection.execute(
        """
        DELETE FROM papers
        WHERE paper_id = ?
        """,
        (paper_id,)
    )

    connection.commit()
    deleted = cursor.rowcount > 0
    connection.close()

    return deleted
