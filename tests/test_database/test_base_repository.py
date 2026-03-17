import pytest


@pytest.fixture
def repository():
    """创建测试用的仓储实例"""
    from database.base_repository import BaseRepository
    return BaseRepository(":memory:")


def test_init(repository):
    """测试仓储初始化"""
    assert repository is not None
    assert repository.db_name == ":memory:"
    assert repository.db_manager is not None


def test_create_table(repository):
    """测试创建表"""
    sql = """
    CREATE TABLE IF NOT EXISTS test_create_table (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        value REAL
    )
    """
    result = repository.create_table(sql)
    assert result is True
    assert repository.table_exists("test_create_table") is True


def test_drop_table(repository):
    """测试删除表"""
    sql = """
    CREATE TABLE IF NOT EXISTS test_drop_table (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )
    """
    repository.create_table(sql)
    
    result = repository.drop_table("test_drop_table")
    assert result is True
    assert repository.table_exists("test_drop_table") is False


def test_insert_one(repository):
    """测试插入单条数据"""
    sql = """
    CREATE TABLE IF NOT EXISTS test_insert_one (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        value REAL
    )
    """
    repository.create_table(sql)
    
    insert_sql = "INSERT INTO test_insert_one (id, name, value) VALUES (?, ?, ?)"
    result = repository.insert(insert_sql, (1, "test", 10.5))
    assert result is True


def test_insert_many(repository):
    """测试插入多条数据"""
    sql = """
    CREATE TABLE IF NOT EXISTS test_insert_many (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        value REAL
    )
    """
    repository.create_table(sql)
    
    insert_sql = "INSERT INTO test_insert_many (id, name, value) VALUES (?, ?, ?)"
    data = [(1, "test1", 10.5), (2, "test2", 20.5), (3, "test3", 30.5)]
    result = repository.insert(insert_sql, data)
    assert result is True


def test_update_one(repository):
    """测试更新单条数据"""
    sql = """
    CREATE TABLE IF NOT EXISTS test_update_one (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        value REAL
    )
    """
    repository.create_table(sql)
    
    insert_sql = "INSERT INTO test_update_one (id, name, value) VALUES (?, ?, ?)"
    repository.insert(insert_sql, (1, "test", 10.5))
    
    update_sql = "UPDATE test_update_one SET value = ? WHERE id = ?"
    result = repository.update(update_sql, (20.5, 1))
    assert result is True


def test_update_many(repository):
    """测试更新多条数据"""
    sql = """
    CREATE TABLE IF NOT EXISTS test_update_many (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        value REAL
    )
    """
    repository.create_table(sql)
    
    insert_sql = "INSERT INTO test_update_many (id, name, value) VALUES (?, ?, ?)"
    repository.insert(insert_sql, [(1, "test1", 10.5), (2, "test2", 20.5)])
    
    update_sql = "UPDATE test_update_many SET value = ? WHERE id = ?"
    data = [(15.5, 1), (25.5, 2)]
    result = repository.update(update_sql, data)
    assert result is True


def test_delete(repository):
    """测试删除数据"""
    sql = """
    CREATE TABLE IF NOT EXISTS test_delete (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )
    """
    repository.create_table(sql)
    
    insert_sql = "INSERT INTO test_delete (id, name) VALUES (?, ?)"
    repository.insert(insert_sql, (1, "test"))
    
    delete_sql = "DELETE FROM test_delete WHERE id = ?"
    result = repository.delete(delete_sql, (1,))
    assert result is True


def test_query_one(repository):
    """测试查询单条数据"""
    sql = """
    CREATE TABLE IF NOT EXISTS test_query_one (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        value REAL
    )
    """
    repository.create_table(sql)
    
    insert_sql = "INSERT INTO test_query_one (id, name, value) VALUES (?, ?, ?)"
    repository.insert(insert_sql, (1, "test", 10.5))
    
    select_sql = "SELECT * FROM test_query_one WHERE id = ?"
    result = repository.query_one(select_sql, (1,))
    assert result is not None
    assert result[0] == 1
    assert result[1] == "test"
    assert result[2] == 10.5


def test_query_one_not_found(repository):
    """测试查询不存在的数据"""
    sql = """
    CREATE TABLE IF NOT EXISTS test_query_one_not_found (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )
    """
    repository.create_table(sql)
    
    select_sql = "SELECT * FROM test_query_one_not_found WHERE id = ?"
    result = repository.query_one(select_sql, (999,))
    assert result is None


def test_query_many(repository):
    """测试查询多条数据"""
    sql = """
    CREATE TABLE IF NOT EXISTS test_query_many (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        value REAL
    )
    """
    repository.create_table(sql)
    
    insert_sql = "INSERT INTO test_query_many (id, name, value) VALUES (?, ?, ?)"
    repository.insert(insert_sql, [(1, "test1", 10.5), (2, "test2", 20.5), (3, "test3", 30.5)])
    
    select_sql = "SELECT * FROM test_query_many ORDER BY id"
    results = repository.query_many(select_sql)
    assert len(results) == 3
    assert results[0][0] == 1
    assert results[1][0] == 2
    assert results[2][0] == 3


def test_query_many_empty(repository):
    """测试查询空结果"""
    sql = """
    CREATE TABLE IF NOT EXISTS test_query_many_empty (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )
    """
    repository.create_table(sql)
    
    select_sql = "SELECT * FROM test_query_many_empty"
    results = repository.query_many(select_sql)
    assert results == []


def test_table_exists(repository):
    """测试检查表是否存在"""
    assert repository.table_exists("non_existent_table") is False
    
    sql = """
    CREATE TABLE IF NOT EXISTS test_table_exists (
        id INTEGER PRIMARY KEY
    )
    """
    repository.create_table(sql)
    assert repository.table_exists("test_table_exists") is True


def test_execute(repository):
    """测试执行 SQL"""
    sql = """
    CREATE TABLE IF NOT EXISTS test_execute (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )
    """
    result = repository.execute(sql)
    assert result is True