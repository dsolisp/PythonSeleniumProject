"""
Enhanced database management with connection pooling,
multiple database support, and comprehensive error handling.
"""

import sqlite3
import threading
import time
from typing import Optional, Dict, Any, List, Union
from contextlib import contextmanager
from dataclasses import dataclass
from queue import Queue, Empty
import json
from pathlib import Path

from config.settings import settings
from utils.logger import test_logger


@dataclass
class DatabaseConfig:
    """Database configuration data class."""
    db_type: str
    connection_string: str
    pool_size: int = 5
    timeout: int = 30
    auto_commit: bool = True


class ConnectionPool:
    """Thread-safe database connection pool."""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.pool = Queue(maxsize=config.pool_size)
        self.active_connections = 0
        self.lock = threading.Lock()
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize the connection pool."""
        for _ in range(self.config.pool_size):
            conn = self._create_connection()
            if conn:
                self.pool.put(conn)
    
    def _create_connection(self) -> Optional[sqlite3.Connection]:
        """Create a new database connection."""
        try:
            if self.config.db_type.lower() == "sqlite":
                conn = sqlite3.connect(
                    self.config.connection_string,
                    check_same_thread=False,
                    timeout=self.config.timeout
                )
                conn.row_factory = sqlite3.Row  # Enable column access by name
                return conn
            else:
                raise ValueError(f"Unsupported database type: {self.config.db_type}")
        except Exception as e:
            test_logger.log_error(e, {"operation": "create_connection"})
            return None
    
    def get_connection(self, timeout: int = 5) -> Optional[sqlite3.Connection]:
        """Get a connection from the pool."""
        try:
            conn = self.pool.get(timeout=timeout)
            with self.lock:
                self.active_connections += 1
            return conn
        except Empty:
            test_logger.logger.warning("Connection pool timeout")
            return None
    
    def return_connection(self, conn: sqlite3.Connection):
        """Return a connection to the pool."""
        if conn:
            try:
                # Reset connection state
                conn.rollback()
                self.pool.put(conn)
                with self.lock:
                    self.active_connections -= 1
            except Exception as e:
                test_logger.log_error(e, {"operation": "return_connection"})
                conn.close()
    
    def close_all(self):
        """Close all connections in the pool."""
        while not self.pool.empty():
            try:
                conn = self.pool.get_nowait()
                conn.close()
            except (Empty, Exception) as e:
                if not isinstance(e, Empty):
                    test_logger.log_error(e, {"operation": "close_all"})
                break


class DatabaseManager:
    """Enhanced database manager with connection pooling and advanced features."""
    
    def __init__(self):
        self.pools: Dict[str, ConnectionPool] = {}
        self.default_pool_name = "default"
        self._setup_default_pool()
    
    def _setup_default_pool(self):
        """Setup the default connection pool."""
        config = DatabaseConfig(
            db_type=settings.db_type,
            connection_string=settings.db_file,
            pool_size=settings.db_pool_size,
            timeout=settings.db_timeout
        )
        self.add_pool(self.default_pool_name, config)
    
    def add_pool(self, name: str, config: DatabaseConfig):
        """Add a new connection pool."""
        self.pools[name] = ConnectionPool(config)
        test_logger.logger.info(f"Database pool '{name}' created")
    
    def get_connection(self, pool_name: str = None) -> Optional[sqlite3.Connection]:
        """Get a database connection from the specified pool."""
        pool_name = pool_name or self.default_pool_name
        if pool_name not in self.pools:
            test_logger.logger.error(f"Pool '{pool_name}' not found")
            return None
        
        return self.pools[pool_name].get_connection()
    
    @contextmanager
    def get_connection_context(self, pool_name: str = None):
        """Context manager for database connections."""
        pool_name = pool_name or self.default_pool_name
        conn = self.get_connection(pool_name)
        
        if not conn:
            raise Exception(f"Could not obtain connection from pool '{pool_name}'")
        
        try:
            yield conn
        finally:
            self.pools[pool_name].return_connection(conn)
    
    def execute_query(
        self, 
        query: str, 
        params: Optional[Union[tuple, dict]] = None,
        pool_name: str = None
    ) -> sqlite3.Cursor:
        """Execute a query and return the cursor."""
        start_time = time.time()
        
        with self.get_connection_context(pool_name) as conn:
            try:
                cursor = conn.cursor()
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                    conn.commit()
                
                duration = time.time() - start_time
                test_logger.log_database_operation(
                    operation=query.split()[0].upper(),
                    table=self._extract_table_name(query),
                    duration=duration * 1000
                )
                
                return cursor
                
            except Exception as e:
                conn.rollback()
                test_logger.log_error(e, {
                    "query": query,
                    "params": params,
                    "operation": "execute_query"
                })
                raise
    
    def execute_many(
        self, 
        query: str, 
        params_list: List[Union[tuple, dict]],
        pool_name: str = None
    ) -> sqlite3.Cursor:
        """Execute a query with multiple parameter sets."""
        start_time = time.time()
        
        with self.get_connection_context(pool_name) as conn:
            try:
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                conn.commit()
                
                duration = time.time() - start_time
                test_logger.log_database_operation(
                    operation=f"{query.split()[0].upper()}_MANY",
                    table=self._extract_table_name(query),
                    duration=duration * 1000
                )
                
                return cursor
                
            except Exception as e:
                conn.rollback()
                test_logger.log_error(e, {
                    "query": query,
                    "params_count": len(params_list),
                    "operation": "execute_many"
                })
                raise
    
    def fetch_one(self, cursor: sqlite3.Cursor) -> Optional[sqlite3.Row]:
        """Fetch a single result from the cursor."""
        try:
            return cursor.fetchone()
        except Exception as e:
            test_logger.log_error(e, {"operation": "fetch_one"})
            return None
    
    def fetch_all(self, cursor: sqlite3.Cursor) -> List[sqlite3.Row]:
        """Fetch all results from the cursor."""
        try:
            return cursor.fetchall()
        except Exception as e:
            test_logger.log_error(e, {"operation": "fetch_all"})
            return []
    
    def fetch_many(self, cursor: sqlite3.Cursor, size: int) -> List[sqlite3.Row]:
        """Fetch a specified number of results from the cursor."""
        try:
            return cursor.fetchmany(size)
        except Exception as e:
            test_logger.log_error(e, {
                "operation": "fetch_many",
                "size": size
            })
            return []
    
    def execute_script(self, script: str, pool_name: str = None):
        """Execute a SQL script."""
        with self.get_connection_context(pool_name) as conn:
            try:
                conn.executescript(script)
                conn.commit()
                test_logger.logger.info("SQL script executed successfully")
            except Exception as e:
                conn.rollback()
                test_logger.log_error(e, {"operation": "execute_script"})
                raise
    
    def backup_database(self, backup_path: str, pool_name: str = None):
        """Create a backup of the database."""
        backup_path = Path(backup_path)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        with self.get_connection_context(pool_name) as conn:
            try:
                backup_conn = sqlite3.connect(str(backup_path))
                conn.backup(backup_conn)
                backup_conn.close()
                
                test_logger.logger.info(f"Database backed up to {backup_path}")
                
            except Exception as e:
                test_logger.log_error(e, {
                    "operation": "backup_database",
                    "backup_path": str(backup_path)
                })
                raise
    
    def restore_database(self, backup_path: str, pool_name: str = None):
        """Restore database from backup."""
        if not Path(backup_path).exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        with self.get_connection_context(pool_name) as conn:
            try:
                backup_conn = sqlite3.connect(backup_path)
                backup_conn.backup(conn)
                backup_conn.close()
                
                test_logger.logger.info(f"Database restored from {backup_path}")
                
            except Exception as e:
                test_logger.log_error(e, {
                    "operation": "restore_database",
                    "backup_path": backup_path
                })
                raise
    
    def get_table_info(self, table_name: str, pool_name: str = None) -> List[Dict[str, Any]]:
        """Get information about a table."""
        query = f"PRAGMA table_info({table_name})"
        cursor = self.execute_query(query, pool_name=pool_name)
        
        columns = []
        for row in self.fetch_all(cursor):
            columns.append({
                "column_id": row["cid"],
                "name": row["name"],
                "type": row["type"],
                "not_null": bool(row["notnull"]),
                "default_value": row["dflt_value"],
                "primary_key": bool(row["pk"])
            })
        
        return columns
    
    def get_table_names(self, pool_name: str = None) -> List[str]:
        """Get all table names in the database."""
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        cursor = self.execute_query(query, pool_name=pool_name)
        
        return [row["name"] for row in self.fetch_all(cursor)]
    
    def table_exists(self, table_name: str, pool_name: str = None) -> bool:
        """Check if a table exists."""
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        cursor = self.execute_query(query, (table_name,), pool_name=pool_name)
        
        return self.fetch_one(cursor) is not None
    
    def get_row_count(self, table_name: str, pool_name: str = None) -> int:
        """Get the number of rows in a table."""
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        cursor = self.execute_query(query, pool_name=pool_name)
        
        result = self.fetch_one(cursor)
        return result["count"] if result else 0
    
    def _extract_table_name(self, query: str) -> str:
        """Extract table name from SQL query."""
        try:
            words = query.strip().split()
            if words[0].upper() in ['SELECT', 'INSERT', 'UPDATE', 'DELETE']:
                for i, word in enumerate(words):
                    if word.upper() in ['FROM', 'INTO', 'UPDATE']:
                        if i + 1 < len(words):
                            return words[i + 1].strip('()')
            return "unknown"
        except Exception:
            return "unknown"
    
    def close_all_connections(self):
        """Close all connection pools."""
        for name, pool in self.pools.items():
            pool.close_all()
            test_logger.logger.info(f"Closed connection pool '{name}'")


# Global database manager instance
db_manager = DatabaseManager()

# Convenience functions for backward compatibility
def get_connection(db_file: str = None) -> sqlite3.Connection:
    """Get a database connection (backward compatibility)."""
    if db_file and db_file != settings.db_file:
        # Create a temporary pool for different database
        config = DatabaseConfig(
            db_type="sqlite",
            connection_string=db_file,
            pool_size=1
        )
        temp_pool = ConnectionPool(config)
        return temp_pool.get_connection()
    
    return db_manager.get_connection()

def execute_query(conn: sqlite3.Connection, query: str, params: Optional[tuple] = None) -> sqlite3.Cursor:
    """Execute a query (backward compatibility)."""
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    return cursor

def fetch_one(cursor: sqlite3.Cursor) -> Optional[sqlite3.Row]:
    """Fetch one result (backward compatibility)."""
    return cursor.fetchone()

def close_connection(conn: sqlite3.Connection):
    """Close a connection (backward compatibility)."""
    if conn:
        conn.close()