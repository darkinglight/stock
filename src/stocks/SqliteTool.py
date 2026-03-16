# -*- coding: utf-8 -*-
import sqlite3
import threading
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SqliteTool:
    """
    简单sqlite数据库工具类
    编写这个类主要是为了封装sqlite，继承此类复用方法
    """
    # 线程本地存储，用于管理每个线程的独立连接
    _thread_local = threading.local()

    def __init__(self, dbname="finance.db"):
        """
        初始化数据库名称（延迟创建连接，首次操作时创建）
        :param dbname: 连接库的名字，注意，以'.db'结尾
        """
        self.dbname = dbname  # 存储数据库名称，不立即创建连接

    def __enter__(self):
        """
        实现上下文管理器的进入方法
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        实现上下文管理器的退出方法，确保连接被关闭
        """
        self.close_con()
        return False  # 不抑制异常

    # 获取当前线程的数据库连接和游标（线程隔离）
    def _get_conn_cur(self):
        if not hasattr(self._thread_local, 'conn'):
            # 首次使用时创建线程专属连接
            self._thread_local.conn = sqlite3.connect(self.dbname)
            self._thread_local.cur = self._thread_local.conn.cursor()
        return self._thread_local.conn, self._thread_local.cur

    def close_con(self):
        """
        关闭当前线程的数据库连接和游标（线程隔离）
        """
        if hasattr(self._thread_local, 'conn'):
            try:
                self._thread_local.cur.close()
                self._thread_local.conn.close()
                # 移除线程本地存储中的连接信息
                del self._thread_local.conn
                del self._thread_local.cur
                logger.info("[connection closed]")
            except Exception as e:
                logger.error("[close connection error]", exc_info=e)

    # 创建数据表
    def create_table(self, sql: str) -> bool:
        """
        创建表
        :param sql: create sql语句
        :return: True表示创建表成功，False表示失败
        """
        try:
            conn, cur = self._get_conn_cur()  # 使用线程本地连接
            cur.execute(sql)
            conn.commit()
            logger.info("[create table success]")
            return True
        except Exception as e:
            logger.error("[create table error]", exc_info=e)
            if hasattr(self._thread_local, 'conn'):
                self._thread_local.conn.rollback()
            return False

    # 删除数据表
    def drop_table(self, sql: str) -> bool:
        """
        删除表
        :param sql: drop sql语句
        :return: True表示删除成功，False表示失败
        """
        try:
            conn, cur = self._get_conn_cur()  # 使用线程本地连接
            cur.execute(sql)
            conn.commit()
            logger.info("[drop table success]")
            return True
        except Exception as e:
            logger.error("[drop table error]", exc_info=e)
            if hasattr(self._thread_local, 'conn'):
                self._thread_local.conn.rollback()
            return False

    # 插入或更新表数据，一次插入或更新一条数据
    def operate_one(self, sql: str, value: tuple) -> bool:
        """
        插入或更新单条表记录
        :param sql: insert语句或update语句
        :param value: 插入或更新的值，形如（）
        :return: True表示插入或更新成功，False表示失败
        """
        try:
            conn, cur = self._get_conn_cur()  # 使用线程本地连接
            cur.execute(sql, value)
            conn.commit()
            if 'INSERT' in sql.upper():
                logger.info("[insert one record success]")
            elif 'UPDATE' in sql.upper():
                logger.info("[update one record success]")
            return True
        except Exception as e:
            logger.error("[insert/update one record error]", exc_info=e)
            if hasattr(self._thread_local, 'conn'):
                self._thread_local.conn.rollback()
            return False

    # 插入或更新表数据，一次插入或更新多条数据
    def operate_many(self, sql: str, value: list) -> bool:
        """
        插入或更新多条表记录
        :param sql: insert语句或update语句
        :param value: 插入或更新的字段的具体值，列表形式为list:[(),()]
        :return: True表示插入或更新成功，False表示失败
        """
        try:
            conn, cur = self._get_conn_cur()  # 使用线程本地连接
            cur.executemany(sql, value)
            conn.commit()
            if 'INSERT' in sql.upper():
                logger.info("[insert many records success]")
            elif 'UPDATE' in sql.upper():
                logger.info("[update many records success]")
            return True
        except Exception as e:
            logger.error("[insert/update many records error]", exc_info=e)
            if hasattr(self._thread_local, 'conn'):
                self._thread_local.conn.rollback()
            return False

    # 删除表数据
    def delete_record(self, sql: str) -> bool:
        """
        删除表记录
        :param sql: 删除记录SQL语句
        :return: True表示删除成功，False表示失败
        """
        try:
            if 'DELETE' in sql.upper():
                conn, cur = self._get_conn_cur()  # 使用线程本地连接
                cur.execute(sql)
                conn.commit()
                logger.info("[delete record success]")
                return True
            else:
                logger.warning("[sql is not delete]")
                return False
        except Exception as e:
            logger.error("[delete record error]", exc_info=e)
            if hasattr(self._thread_local, 'conn'):
                self._thread_local.conn.rollback()
            return False

    # 查询一条数据
    def query_one(self, sql: str, params=None) -> tuple:
        """
        查询单条数据
        :param sql: select语句
        :param params: 查询参数，形如()
        :return: 语句查询单条结果，None表示查询失败
        """
        try:
            conn, cur = self._get_conn_cur()  # 使用线程本地连接
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)
            r = cur.fetchone()
            logger.info("[select one record success]")
            return r
        except Exception as e:
            logger.error("[select one record error]", exc_info=e)
            return None

    # 查询多条数据
    def query_many(self, sql: str, params=None) -> list:
        """
        查询多条数据
        :param sql: select语句
        :param params: 查询参数，形如()
        :return: 语句查询多条结果，空列表表示查询失败
        """
        try:
            conn, cur = self._get_conn_cur()  # 使用线程本地连接
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)
            r = cur.fetchall()
            logger.info("[select many records success]")
            return r
        except Exception as e:
            logger.error("[select many records error]", exc_info=e)
            return []

    def table_exist(self, table_name: str) -> bool:
        """
        检查表是否存在
        :param table_name: 表名
        :return: True表示表存在，False表示表不存在
        """
        try:
            conn, cur = self._get_conn_cur()  # 使用线程本地连接
            # 使用参数化查询，避免SQL注入
            cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            return cur.fetchone()[0] == 1
        except Exception as e:
            logger.error("[check table exist error]", exc_info=e)
            return False


if __name__ == '__main__':
    # 创建数据表info的SQL语句
    create_tb_sql = ("create table if not exists info("
                     "id  int  primary key,"
                     "name text not null,"
                     "age int not null,"
                     "address char(50));")
    
    # 使用上下文管理器
    with SqliteTool() as mySqlite:
        # 创建数据表
        mySqlite.create_table(create_tb_sql)
        # 插入数据
        # 一次插入一条数据
        mySqlite.operate_one('insert into info values(?,?,?)', (4, 'Tom3', 22))
        # 一次插入多条数据
        mySqlite.operate_many('insert into info values(?,?,?)', [
            (5, 'Alice', 22),
            (6, 'John', 21)])
        # 更新数据SQL语句
        update_sql = "update info set age=? where name=?"
        update_value = (22, 'Tom')
        update_values = [(22, 'Tom'), (32, 'John')]
        # 一次更新一条数据
        mySqlite.operate_one(update_sql, update_value)
        # 一次更新多条数据
        mySqlite.operate_many(update_sql, update_values)
        # 查询数据
        select_sql = "select name from info where age =? and name = ?"
        result_many = mySqlite.query_many(select_sql, (23, 'Tom'))
        print(result_many)
        # 删除数据
        delete_sql = "delete from info where name = 'Tom'"
        mySqlite.delete_record(delete_sql)
    
    # 连接会在with语句结束时自动关闭
    print("Connection closed automatically")