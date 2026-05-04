"""
Hybrid DB Testing Patterns
Equivalent to Cypress database.cy.ts.
Demonstrates 5 patterns for combining UI automation with a local SQLite database.
"""

import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

from components.header_component import HeaderComponent
from config.constants import PATHS
from pages.sauce.inventory_page import InventoryPage
from pages.sauce.login_page import LoginPage
from utils.builders.user_builder import UserBuilder


@pytest.mark.database
@pytest.mark.api
class TestDatabase:
    """Database query and validation tests."""

    @pytest.fixture(scope="class", autouse=True)
    def setup_database(self):
        # Database seeding is handled via PythonSeleniumProject/scripts/seed_db.py
        script_path = Path(__file__).parent.parent.parent / "scripts" / "seed_db.py"
        subprocess.run([sys.executable, str(script_path)], check=True)

    @pytest.fixture
    def db_connection(self):
        conn = sqlite3.connect(PATHS.DB)
        yield conn
        conn.close()

    # ── Example 1: Seed → Login (Precondition) ──────────────────────────
    def test_example_1_seeds_user_then_login(self, selenium_driver, db_connection):
        test_user = {"id": 101, "username": "db_user", "password": "password123"}
        cursor = db_connection.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO users VALUES (?, ?, ?)",
            (test_user["id"], test_user["username"], "customer"),
        )
        db_connection.commit()

        login_page = LoginPage(selenium_driver)
        login_page.open()
        login_page.login(test_user["username"], test_user["password"])

        assert login_page.get_error_message()
        assert "do not match" in login_page.get_error_message()

    # ── Example 2: UI Action → DB Verification (Postcondition) ──────────
    def test_example_2_login_then_verify_db(self, selenium_driver, db_connection):
        user = UserBuilder().standard().build()

        login_page = LoginPage(selenium_driver)
        login_page.open()
        login_page.login(user.username, user.password)
        assert "inventory.html" in selenium_driver.current_url

        cursor = db_connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (user.username,))
        rows = cursor.fetchall()
        assert len(rows) == 1
        assert rows[0][2] is not None

    # ── Example 3: DB Data → UI Assertion (Data-Driven) ─────────────────
    def test_example_3_verify_ui_price_matches_db(self, selenium_driver, db_connection):
        cursor = db_connection.cursor()
        cursor.execute(
            "SELECT price FROM products WHERE name=?", ("Sauce Labs Backpack",)
        )
        db_price = cursor.fetchone()[0]

        user = UserBuilder().standard().build()
        login_page = LoginPage(selenium_driver)
        login_page.open()
        login_page.login(user.username, user.password)

        inventory_page = InventoryPage(selenium_driver)
        price_text = inventory_page.get_item_prices()[0]
        assert str(db_price) in price_text

    # ── Example 4: Data-Driven Login (Iterate from DB) ───────────────────
    def test_example_4_login_every_customer(self, selenium_driver, db_connection):
        cursor = db_connection.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE role=? AND username != ?",
            ("customer", "db_user"),
        )
        users = cursor.fetchall()

        for user in users:
            username = user[1]
            login_page = LoginPage(selenium_driver)
            login_page.open()
            login_page.login(username, UserBuilder().standard().build().password)
            assert "inventory.html" in selenium_driver.current_url

            # Logout
            header = HeaderComponent(selenium_driver)
            header.logout()

    # ── Example 5: CRUD Lifecycle ─────────────────────────────────────────
    def test_example_5_crud_lifecycle_in_db(self, db_connection):
        new_user_id = 999
        cursor = db_connection.cursor()

        # Create
        cursor.execute(
            "INSERT OR REPLACE INTO users VALUES (?, ?, ?)",
            (new_user_id, "test_cleanup_user", "tester"),
        )
        db_connection.commit()

        # Read
        cursor.execute("SELECT * FROM users WHERE id=?", (new_user_id,))
        rows = cursor.fetchall()
        assert len(rows) == 1
        assert rows[0][1] == "test_cleanup_user"

        # Delete
        cursor.execute("DELETE FROM users WHERE id=?", (new_user_id,))
        db_connection.commit()

        # Verify deletion
        cursor.execute("SELECT * FROM users WHERE id=?", (new_user_id,))
        rows = cursor.fetchall()
        assert len(rows) == 0
