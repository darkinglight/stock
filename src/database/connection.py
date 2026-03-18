import sqlite3
import threading
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class DatabaseConnectionManager:
    """
    数据库连接管理器
    - 每个线程独立连接
    - 延迟创建连接
    - 自动释放连接
    - 线程安全
    """
    
    _instance: Optional['DatabaseConnectionManager'] = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    # 使用threading.local()存储线程本地连接
                    cls._instance._local = threading.local()
                    logger.info("DatabaseConnectionManager instance created")
        return cls._instance
    
    def _get_thread_connections(self) -> Dict[str, sqlite3.Connection]:
        """
        获取当前线程的连接字典
        :return: 当前线程的连接字典
        """
        if not hasattr(self._local, 'connections'):
            self._local.connections = {}
        return self._local.connections
    
    def get_connection(self, db_name: str = "finance.db") -> sqlite3.Connection:
        """
        获取数据库连接，如果不存在则创建
        :param db_name: 数据库名称
        :return: 数据库连接对象
        """
        connections = self._get_thread_connections()
        if db_name not in connections:
            try:
                # 为每个线程创建独立连接
                conn = sqlite3.connect(db_name)
                conn.row_factory = sqlite3.Row
                connections[db_name] = conn
                logger.info(f"Created new connection for database {db_name} in thread {threading.current_thread().name}")
            except Exception as e:
                logger.error(f"Failed to create connection for {db_name}: {e}")
                raise
        return connections[db_name]
    
    def close_connection(self, db_name: str):
        """
        关闭指定数据库连接
        :param db_name: 数据库名称
        """
        connections = self._get_thread_connections()
        if db_name in connections:
            try:
                connections[db_name].close()
                del connections[db_name]
                logger.info(f"Closed connection for database {db_name} in thread {threading.current_thread().name}")
            except Exception as e:
                logger.error(f"Failed to close connection for {db_name}: {e}")
    
    def close_all(self):
        """
        关闭当前线程的所有数据库连接
        """
        connections = self._get_thread_connections()
        for db_name, conn in list(connections.items()):
            try:
                conn.close()
                logger.info(f"Closed connection for database {db_name} in thread {threading.current_thread().name}")
            except Exception as e:
                logger.error(f"Failed to close connection for {db_name}: {e}")
        connections.clear()
        logger.info(f"All database connections closed in thread {threading.current_thread().name}")
    
    def get_cursor(self, db_name: str = "finance.db") -> sqlite3.Cursor:
        """
        获取数据库游标
        :param db_name: 数据库名称
        :return: 数据库游标对象
        """
        conn = self.get_connection(db_name)
        return conn.cursor()