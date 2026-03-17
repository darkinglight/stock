import sqlite3
import threading
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class DatabaseConnectionManager:
    """
    数据库连接管理器
    - 延迟创建连接
    - 连接复用，减少重连
    - 自动释放连接
    - 线程安全
    """
    
    _instance: Optional['DatabaseConnectionManager'] = None
    _connections: Dict[str, sqlite3.Connection] = {}
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    logger.info("DatabaseConnectionManager instance created")
        return cls._instance
    
    def get_connection(self, db_name: str = "finance.db") -> sqlite3.Connection:
        """
        获取数据库连接，如果不存在则创建
        :param db_name: 数据库名称
        :return: 数据库连接对象
        """
        if db_name not in self._connections:
            with self._lock:
                if db_name not in self._connections:
                    try:
                        conn = sqlite3.connect(db_name, check_same_thread=False)
                        conn.row_factory = sqlite3.Row
                        self._connections[db_name] = conn
                        logger.info(f"Created new connection for database: {db_name}")
                    except Exception as e:
                        logger.error(f"Failed to create connection for {db_name}: {e}")
                        raise
        return self._connections[db_name]
    
    def close_connection(self, db_name: str):
        """
        关闭指定数据库连接
        :param db_name: 数据库名称
        """
        if db_name in self._connections:
            with self._lock:
                if db_name in self._connections:
                    try:
                        self._connections[db_name].close()
                        del self._connections[db_name]
                        logger.info(f"Closed connection for database: {db_name}")
                    except Exception as e:
                        logger.error(f"Failed to close connection for {db_name}: {e}")
    
    def close_all(self):
        """
        关闭所有数据库连接
        """
        with self._lock:
            for db_name, conn in list(self._connections.items()):
                try:
                    conn.close()
                    logger.info(f"Closed connection for database: {db_name}")
                except Exception as e:
                    logger.error(f"Failed to close connection for {db_name}: {e}")
            self._connections.clear()
            logger.info("All database connections closed")
    
    def get_cursor(self, db_name: str = "finance.db") -> sqlite3.Cursor:
        """
        获取数据库游标
        :param db_name: 数据库名称
        :return: 数据库游标对象
        """
        conn = self.get_connection(db_name)
        return conn.cursor()