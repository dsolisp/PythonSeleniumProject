import sqlite3
from pathlib import Path


def seed(conn) -> None:
    """
    Seed the database using a DB-API connection.

    This is intentionally DB-agnostic (SQLite/Postgres/etc.) so tests can provide
    an isolated connection per test/class without writing shared state to disk.
    """
    cursor = conn.cursor()

    # Make reseeding idempotent across DB engines (SQLite/Postgres).
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS products")

    cursor.execute("CREATE TABLE users (id INT, username TEXT, role TEXT)")
    cursor.execute(
        "INSERT INTO users (id, username, role) VALUES (1, 'standard_user', 'customer')"
    )
    cursor.execute(
        "INSERT INTO users (id, username, role) VALUES (2, 'admin_user', 'admin')"
    )

    cursor.execute("CREATE TABLE products (id INT, name TEXT, price REAL)")
    cursor.execute(
        "INSERT INTO products (id, name, price) VALUES (1, 'Sauce Labs Backpack', 29.99)"
    )
    conn.commit()


def seed_sqlite_file(db_path: Path) -> None:
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(str(db_path))
    try:
        seed(conn)
    finally:
        conn.close()
    print("✅ Python Database Seeded.")


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    seed_sqlite_file(project_root / "app.db")
