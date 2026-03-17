import pytest
import sqlite3
import threading


@pytest.fixture
def db_manager():
    """创建独立的数据库连接管理器实例"""
    from database.connection import DatabaseConnectionManager
    
    manager = DatabaseConnectionManager()
    yield manager
    
    manager.close_all()


def test_get_connection(db_manager):
    """测试获取数据库连接"""
    conn = db_manager.get_connection(":memory:")
    
    assert conn is not None
    assert isinstance(conn, sqlite3.Connection)
    assert conn.cursor() is not None


def test_connection_reuse(db_manager):
    """测试连接复用"""
    conn1 = db_manager.get_connection(":memory:")
    conn2 = db_manager.get_connection(":memory:")
    
    assert conn1 is conn2


def test_close_connection(db_manager):
    """测试关闭指定数据库连接"""
    conn = db_manager.get_connection(":memory:")
    db_manager.close_connection(":memory:")
    
    assert len(db_manager._connections) == 0


def test_close_all(db_manager):
    """测试关闭所有数据库连接"""
    db_manager.get_connection(":memory:")
    db_manager.get_connection("test.db")
    db_manager.close_all()
    
    assert len(db_manager._connections) == 0


def test_singleton():
    """测试单例模式"""
    from database.connection import DatabaseConnectionManager
    
    db_manager1 = DatabaseConnectionManager()
    db_manager2 = DatabaseConnectionManager()
    
    assert db_manager1 is db_manager2


def test_get_cursor(db_manager):
    """测试获取数据库游标"""
    cursor = db_manager.get_cursor(":memory:")
    
    assert cursor is not None
    assert hasattr(cursor, 'execute')


def test_multiple_databases(db_manager):
    """测试多个数据库连接"""
    conn1 = db_manager.get_connection("db1.db")
    conn2 = db_manager.get_connection("db2.db")
    
    assert conn1 is not None
    assert conn2 is not None
    assert conn1 is not conn2
    assert len(db_manager._connections) == 2


def test_thread_safety(db_manager):
    """测试线程安全"""
    results = []
    
    def get_connection():
        conn = db_manager.get_connection(":memory:")
        results.append(conn)
    
    threads = []
    for i in range(10):
        t = threading.Thread(target=get_connection)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    assert len(results) == 10
    assert all(conn is results[0] for conn in results)