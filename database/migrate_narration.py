"""
Migration: add narration_text to scenes
DGX AI Movie Studio

Adds a `narration_text` column so a scene's SPOKEN line is stored separately
from its IMAGE PROMPT. They serve different purposes:

    description     -> fed to SDXL   (keywords, style tags, camera language)
    narration_text  -> fed to Piper  (a sentence a narrator would actually say)

Safe to run more than once. Run from the project root:
    python -m database.migrate_narration
"""

from config.database import get_connection


def column_exists(conn, table, column):
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(r[1] == column for r in rows)


def main():
    conn = get_connection()
    try:
        if column_exists(conn, "scenes", "narration_text"):
            print("scenes.narration_text already exists — nothing to do.")
            return

        print("Adding scenes.narration_text ...")
        conn.execute("ALTER TABLE scenes ADD COLUMN narration_text TEXT")
        conn.commit()
        print("Done.")

        # Backfill: existing scenes get a clean spoken line derived from their
        # title, rather than the style-tag-laden image prompt.
        rows = conn.execute(
            "SELECT id, title FROM scenes WHERE narration_text IS NULL"
        ).fetchall()

        for row in rows:
            title = (row[1] or "").split(":", 1)[-1].strip()
            conn.execute(
                "UPDATE scenes SET narration_text = ? WHERE id = ?",
                (title, row[0]),
            )
        conn.commit()
        print(f"Backfilled {len(rows)} existing scene(s).")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
