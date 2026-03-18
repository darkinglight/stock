from typing import Optional, List, Union, Any
from .connection import DatabaseConnectionManager
import logging

logger = logging.getLogger(__name__)


class BaseRepository:
    """
    基础仓储类
    提供通用的数据库操作方法
    """
    
    def __init__(self, db_name: str = "finance.db"):
        """
        初始化仓储
        :param db_name: 数据库名称
        """
        self.db_name = db_name
        self.db_manager = DatabaseConnectionManager()
    
    def create_table(self, sql: str) -> bool:
        """
        创建表
        :param sql: CREATE TABLE SQL 语句
        :return: 是否成功
        """
        try:
            conn = self.db_manager.get_connection(self.db_name)
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            logger.info("Table created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create table: {e}")
            return False
    
    def drop_table(self, table_name: str) -> bool:
        """
        删除表
        :param table_name: 表名
        :return: 是否成功
        """
        try:
            sql = f"DROP TABLE IF EXISTS {table_name}"
            conn = self.db_manager.get_connection(self.db_name)
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            logger.info(f"Table {table_name} dropped successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to drop table {table_name}: {e}")
            return False
    
    def insert(self, sql: str, data: Union[tuple, list]) -> bool:
        """
        插入数据
        :param sql: INSERT SQL 语句
        :param data: 插入的数据
        :return: 是否成功
        """
        try:
            conn = self.db_manager.get_connection(self.db_name)
            cursor = conn.cursor()
            if isinstance(data, list):
                cursor.executemany(sql, data)
            else:
                cursor.execute(sql, data)
            conn.commit()
            logger.info("Data inserted successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to insert data: {e}")
            try:
                conn.rollback()
            except:
                pass
            return False
    
    def update(self, sql: str, data: Union[tuple, list]) -> bool:
        """
        更新数据
        :param sql: UPDATE SQL 语句
        :param data: 更新的数据
        :return: 是否成功
        """
        try:
            conn = self.db_manager.get_connection(self.db_name)
            cursor = conn.cursor()
            if isinstance(data, list):
                cursor.executemany(sql, data)
            else:
                cursor.execute(sql, data)
            conn.commit()
            logger.info("Data updated successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to update data: {e}")
            try:
                conn.rollback()
            except:
                pass
            return False
    
    def delete(self, sql: str, params: tuple = None) -> bool:
        """
        删除数据
        :param sql: DELETE SQL 语句
        :param params: 删除参数
        :return: 是否成功
        """
        try:
            conn = self.db_manager.get_connection(self.db_name)
            cursor = conn.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            conn.commit()
            logger.info("Data deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to delete data: {e}")
            try:
                conn.rollback()
            except:
                pass
            return False
    
    def query_one(self, sql: str, params: tuple = None) -> Optional[tuple]:
        """
        查询单条数据
        :param sql: SELECT SQL 语句
        :param params: 查询参数
        :return: 查询结果
        """
        try:
            conn = self.db_manager.get_connection(self.db_name)
            cursor = conn.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            result = cursor.fetchone()
            return result
        except Exception as e:
            logger.error(f"Failed to query one: {e}")
            return None
    
    def query_many(self, sql: str, params: tuple = None) -> List[tuple]:
        """
        查询多条数据
        :param sql: SELECT SQL 语句
        :param params: 查询参数
        :return: 查询结果列表
        """
        try:
            conn = self.db_manager.get_connection(self.db_name)
            cursor = conn.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            results = cursor.fetchall()
            return results
        except Exception as e:
            logger.error(f"Failed to query many: {e}")
            return []
    
    def execute(self, sql: str, params: tuple = None) -> bool:
        """
        执行 SQL 语句
        :param sql: SQL 语句
        :param params: 参数
        :return: 是否成功
        """
        try:
            conn = self.db_manager.get_connection(self.db_name)
            cursor = conn.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to execute SQL: {e}")
            try:
                conn.rollback()
            except:
                pass
            return False
    
    def table_exists(self, table_name: str) -> bool:
        """
        检查表是否存在
        :param table_name: 表名
        :return: 是否存在
        """
        sql = "SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?"
        result = self.query_one(sql, (table_name,))
        return result[0] == 1 if result else False
