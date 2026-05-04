import os
import sqlite3
from pathlib import Path


def seed():
    project_root = Path(__file__).resolve().parent.parent
    db_path = project_root / "app.db"

    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (id INT, username TEXT, role TEXT)")
    cursor.execute(
        "INSERT INTO users VALUES (?, ?, ?)", (1, "standard_user", "customer")
    )
    cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (2, "admin_user", "admin"))

    cursor.execute("CREATE TABLE products (id INT, name TEXT, price REAL)")
    cursor.execute(
        "INSERT INTO products VALUES (?, ?, ?)", (1, "Sauce Labs Backpack", 29.99)
    )
    conn.commit()
    conn.close()
    print("✅ Python Database Seeded.")


if __name__ == "__main__":
    seed()
