from typing import Optional, List, TypeVar, Type
from .connection import DatabaseConnectionManager
from .entity import BaseEntity
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseEntity)


class BaseRepository:
    """
    基础仓储类
    提供通用的数据库操作方法
    支持直接操作 Entity 对象
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
            conn.rollback()
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
            conn.rollback()
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
            conn.rollback()
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
            conn.rollback()
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
    
    def save(self, entity: T) -> bool:
        """
        保存单个 Entity 对象
        :param entity: Entity 对象
        :return: 是否成功
        """
        try:
            table_name = entity.get_table_name()
            field_names = entity.get_field_names()
            
            if not field_names:
                logger.warning(f"Entity {entity.__class__.__name__} has no fields")
                return False
            
            values = [getattr(entity, field) for field in field_names]
            placeholders = ", ".join(["?" for _ in field_names])
            
            sql = f"""
            INSERT INTO {table_name} ({", ".join(field_names)})
            VALUES ({placeholders})
            ON CONFLICT({field_names[0]}) DO UPDATE SET
                {", ".join([f"{field}=excluded.{field}" for field in field_names[1:]])}
            """
            
            return self.insert(sql, tuple(values))
        except Exception as e:
            logger.error(f"Failed to save entity: {e}")
            return False
    
    def save_all(self, entities: List[T]) -> int:
        """
        批量保存 Entity 对象列表
        :param entities: Entity 对象列表
        :return: 成功保存的数量
        """
        if not entities:
            return 0
        
        try:
            table_name = entities[0].get_table_name()
            field_names = entities[0].get_field_names()
            
            if not field_names:
                logger.warning(f"Entity {entities[0].__class__.__name__} has no fields")
                return 0
            
            values_list = []
            for entity in entities:
                values = [getattr(entity, field) for field in field_names]
                values_list.append(tuple(values))
            
            sql = f"""
            INSERT INTO {table_name} ({", ".join(field_names)})
            VALUES ({", ".join(["?" for _ in field_names])})
            ON CONFLICT({field_names[0]}) DO UPDATE SET
                {", ".join([f"{field}=excluded.{field}" for field in field_names[1:]])}
            """
            
            return self.insert(sql, values_list)
        except Exception as e:
            logger.error(f"Failed to save all entities: {e}")
            return 0
    
    def update_entity(self, entity: T) -> bool:
        """
        更新单个 Entity 对象
        :param entity: Entity 对象
        :return: 是否成功
        """
        try:
            table_name = entity.get_table_name()
            field_names = entity.get_field_names()
            
            if not field_names:
                logger.warning(f"Entity {entity.__class__.__name__} has no fields")
                return False
            
            pk_field = field_names[0]
            pk_value = getattr(entity, pk_field)
            
            update_fields = field_names[1:]
            set_clause = ", ".join([f"{field}=?" for field in update_fields])
            
            values = [getattr(entity, field) for field in update_fields]
            
            sql = f"""
            UPDATE {table_name}
            SET {set_clause}
            WHERE {pk_field} = ?
            """
            
            return self.update(sql, tuple(values + [pk_value]))
        except Exception as e:
            logger.error(f"Failed to update entity: {e}")
            return False
    
    def update_all(self, entities: List[T]) -> int:
        """
        批量更新 Entity 对象列表
        :param entities: Entity 对象列表
        :return: 成功更新的数量
        """
        if not entities:
            return 0
        
        try:
            table_name = entities[0].get_table_name()
            field_names = entities[0].get_field_names()
            
            if not field_names:
                logger.warning(f"Entity {entities[0].__class__.__name__} has no fields")
                return 0
            
            pk_field = field_names[0]
            update_fields = field_names[1:]
            set_clause = ", ".join([f"{field}=?" for field in update_fields])
            
            values_list = []
            for entity in entities:
                pk_value = getattr(entity, pk_field)
                update_values = [getattr(entity, field) for field in update_fields]
                values_list.append(tuple(update_values + [pk_value]))
            
            sql = f"""
            UPDATE {table_name}
            SET {set_clause}
            WHERE {pk_field} = ?
            """
            
            return self.update(sql, values_list)
        except Exception as e:
            logger.error(f"Failed to update all entities: {e}")
            return 0
    
    def delete_entity(self, entity: T) -> bool:
        """
        删除单个 Entity 对象
        :param entity: Entity 对象
        :return: 是否成功
        """
        try:
            table_name = entity.get_table_name()
            field_names = entity.get_field_names()
            
            if not field_names:
                logger.warning(f"Entity {entity.__class__.__name__} has no fields")
                return False
            
            pk_field = field_names[0]
            pk_value = getattr(entity, pk_field)
            
            sql = f"DELETE FROM {table_name} WHERE {pk_field} = ?"
            
            return self.delete(sql, (pk_value,))
        except Exception as e:
            logger.error(f"Failed to delete entity: {e}")
            return False
    
    def find_by_id(self, entity_class: Type[T], pk_value: Any) -> Optional[T]:
        """
        根据主键查找 Entity
        :param entity_class: Entity 类
        :param pk_value: 主键值
        :return: Entity 对象或 None
        """
        try:
            table_name = entity_class.get_table_name()
            field_names = entity_class.get_field_names()
            
            if not field_names:
                logger.warning(f"Entity {entity_class.__name__} has no fields")
                return None
            
            pk_field = field_names[0]
            sql = f"SELECT * FROM {table_name} WHERE {pk_field} = ?"
            
            result = self.query_one(sql, (pk_value,))
            if result:
                return entity_class.from_dict(dict(zip(field_names, result)))
            return None
        except Exception as e:
            logger.error(f"Failed to find entity by id: {e}")
            return None
    
    def find_all(self, entity_class: Type[T], **kwargs) -> List[T]:
        """
        查找所有 Entity
        :param entity_class: Entity 类
        :param kwargs: 查询条件
        :return: Entity 对象列表
        """
        try:
            table_name = entity_class.get_table_name()
            field_names = entity_class.get_field_names()
            
            if not field_names:
                logger.warning(f"Entity {entity_class.__name__} has no fields")
                return []
            
            where_clauses = []
            params = []
            
            for key, value in kwargs.items():
                where_clauses.append(f"{key} = ?")
                params.append(value)
            
            where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
            sql = f"SELECT * FROM {table_name} WHERE {where_clause}"
            
            results = self.query_many(sql, tuple(params) if params else None)
            
            return [entity_class.from_dict(dict(zip(field_names, row))) for row in results]
        except Exception as e:
            logger.error(f"Failed to find all entities: {e}")
            return []
    
    def exists(self, entity: T) -> bool:
        """
        检查 Entity 是否存在
        :param entity: Entity 对象
        :return: 是否存在
        """
        try:
            table_name = entity.get_table_name()
            field_names = entity.get_field_names()
            
            if not field_names:
                logger.warning(f"Entity {entity.__class__.__name__} has no fields")
                return False
            
            pk_field = field_names[0]
            pk_value = getattr(entity, pk_field)
            
            sql = f"SELECT COUNT(*) FROM {table_name} WHERE {pk_field} = ?"
            result = self.query_one(sql, (pk_value,))
            
            return result[0] > 0 if result else False
        except Exception as e:
            logger.error(f"Failed to check entity exists: {e}")
            return False