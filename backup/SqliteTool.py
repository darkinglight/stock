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

    # 执行SQL语句
    def _execute_sql(self, sql, params=None, many=False):
        """
        执行SQL语句
        :param sql: SQL语句
        :param params: 参数
        :param many: 是否执行多条
        :return: 游标对象
        """
        conn, cur = self._get_conn_cur()
        if many:
            cur.executemany(sql, params)
        elif params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)
        return conn, cur

    # 处理查询结果
    def _handle_query_result(self, cur, sql):
        """
        处理查询结果
        :param cur: 游标对象
        :param sql: SQL语句
        :return: 查询结果
        """
        if 'LIMIT 1' in sql.upper() or self._is_single_query(sql):
            result = cur.fetchone()
            logger.info("[select one record success]")
        else:
            result = cur.fetchall()
            logger.info("[select many records success]")
        return result

    # 判断是否为单条查询
    def _is_single_query(self, sql):
        """
        判断是否为单条查询
        :param sql: SQL语句
        :return: 是否为单条查询
        """
        # 简单判断，实际应用中可能需要更复杂的逻辑
        return False

    # 处理非查询操作
    def _handle_non_query(self, conn, sql):
        """
        处理非查询操作
        :param conn: 连接对象
        :param sql: SQL语句
        :return: 是否成功
        """
        conn.commit()
        if 'INSERT' in sql.upper():
            logger.info("[insert record success]")
        elif 'UPDATE' in sql.upper():
            logger.info("[update record success]")
        elif 'DELETE' in sql.upper():
            logger.info("[delete record success]")
        elif 'CREATE' in sql.upper():
            logger.info("[create table success]")
        elif 'DROP' in sql.upper():
            logger.info("[drop table success]")
        return True

    # 通用执行方法，处理异常和事务
    def _execute(self, sql, params=None, many=False, is_query=False):
        """
        通用SQL执行方法
        :param sql: SQL语句
        :param params: 参数
        :param many: 是否执行多条
        :param is_query: 是否为查询操作
        :return: 执行结果
        """
        try:
            conn, cur = self._execute_sql(sql, params, many)
            
            if is_query:
                return self._handle_query_result(cur, sql)
            else:
                return self._handle_non_query(conn, sql)
        except Exception as e:
            logger.error(f"[execute error] {sql}", exc_info=e)
            if hasattr(self._thread_local, 'conn') and not is_query:
                self._thread_local.conn.rollback()
            return None if is_query else False

    # 创建数据表
    def create_table(self, sql: str) -> bool:
        """
        创建表
        :param sql: create sql语句
        :return: True表示创建表成功，False表示失败
        """
        return self._execute(sql)

    # 删除数据表
    def drop_table(self, sql: str) -> bool:
        """
        删除表
        :param sql: drop sql语句
        :return: True表示删除成功，False表示失败
        """
        return self._execute(sql)

    # 插入或更新表数据，一次插入或更新一条数据
    def operate_one(self, sql: str, value: tuple) -> bool:
        """
        插入或更新单条表记录
        :param sql: insert语句或update语句
        :param value: 插入或更新的值，形如（）
        :return: True表示插入或更新成功，False表示失败
        """
        return self._execute(sql, value)

    # 插入或更新表数据，一次插入或更新多条数据
    def operate_many(self, sql: str, value: list) -> bool:
        """
        插入或更新多条表记录
        :param sql: insert语句或update语句
        :param value: 插入或更新的字段的具体值，列表形式为list:[(),()]
        :return: True表示插入或更新成功，False表示失败
        """
        return self._execute(sql, value, many=True)

    # 删除表数据
    def delete_record(self, sql: str) -> bool:
        """
        删除表记录
        :param sql: 删除记录SQL语句
        :return: True表示删除成功，False表示失败
        """
        if 'DELETE' in sql.upper():
            return self._execute(sql)
        else:
            logger.warning("[sql is not delete]")
            return False

    # 查询一条数据
    def query_one(self, sql: str, params=None) -> tuple:
        """
        查询单条数据
        :param sql: select语句
        :param params: 查询参数，形如()
        :return: 语句查询单条结果，None表示查询失败
        """
        return self._execute(sql, params, is_query=True)

    # 查询多条数据
    def query_many(self, sql: str, params=None) -> list:
        """
        查询多条数据
        :param sql: select语句
        :param params: 查询参数，形如()
        :return: 语句查询多条结果，空列表表示查询失败
        """
        result = self._execute(sql, params, is_query=True)
        return result if result is not None else []

    def table_exist(self, table_name: str) -> bool:
        """
        检查表是否存在
        :param table_name: 表名
        :return: True表示表存在，False表示表不存在
        """
        result = self._execute(
            "SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
            is_query=True
        )
        return result[0] == 1 if result else False


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
        mySqlite.operate_one('insert into info values(?,?,?,?)', (4, 'Tom3', 22, 'Beijing'))
        # 一次插入多条数据
        mySqlite.operate_many('insert into info values(?,?,?,?)', [
            (5, 'Alice', 22, 'Shanghai'),
            (6, 'John', 21, 'Guangzhou')])
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
        delete_sql = "delete from info"
        mySqlite.delete_record(delete_sql)
    
    # 连接会在with语句结束时自动关闭
    print("Connection closed automatically")
