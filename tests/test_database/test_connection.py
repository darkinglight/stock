import pytest
import sqlite3
import threading


@pytest.fixture
def db_manager():
    """创建独立的数据库连接管理器实例"""
    from src.database.connection import DatabaseConnectionManager
    
    manager = DatabaseConnectionManager()
    yield manager
    
    manager.close_all()


def test_get_connection(db_manager):
    """测试获取数据库连接"""
    conn = db_manager.get_connection(":memory:")
    
    assert conn is not None
    assert isinstance(conn, sqlite3.Connection)
    assert conn.cursor() is not None


def test_get_cursor(db_manager):
    """测试获取数据库游标"""
    cursor = db_manager.get_cursor(":memory:")
    
    assert cursor is not None
    assert hasattr(cursor, 'execute')


def test_singleton():
    """测试单例模式"""
    from src.database.connection import DatabaseConnectionManager
    
    db_manager1 = DatabaseConnectionManager()
    db_manager2 = DatabaseConnectionManager()
    
    assert db_manager1 is db_manager2


def test_thread_independent_connections():
    """测试线程独立连接"""
    from src.database.connection import DatabaseConnectionManager
    
    db_manager = DatabaseConnectionManager()
    connections = []
    
    def get_connection():
        conn = db_manager.get_connection(":memory:")
        connections.append(conn)
    
    threads = []
    for i in range(3):
        t = threading.Thread(target=get_connection)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    assert len(connections) == 3
    # 每个线程应该有独立的连接
    assert connections[0] is not connections[1]
    assert connections[1] is not connections[2]
    assert connections[0] is not connections[2]


def test_close_all(db_manager):
    """测试关闭所有数据库连接"""
    # 测试关闭方法不会抛出异常
    try:
        db_manager.close_all()
    except Exception as e:
        pytest.fail(f"close_all() raised {e} unexpectedly")
