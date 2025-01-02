from collections import namedtuple

import akshare as ak

from stocks.SqliteTool import SqliteTool

HKStock = namedtuple("HKStock", ['code', 'name', 'price'])


def init_table():
    # 创建数据表info的SQL语句
    create_tb_sql = ("create table if not exists hk_stock("
                     "code text primary key,"
                     "name text,"
                     "price float"
                     ");")
    sqliteTool = SqliteTool()
    # 创建数据表
    sqliteTool.create_table(create_tb_sql)
    sqliteTool.close_con()


def drop_table():
    sqliteTool = SqliteTool()
    sqliteTool.drop_table("drop table hk_stock;")
    sqliteTool.close_con()


def init_hk_stock():
    # 获取数据
    df = ak.stock_hk_ggt_components_em()
    df = df[["代码", "名称", "最新价"]]
    sql = 'insert into hk_stock values(?,?,?)'
    sqliteTool = SqliteTool()
    sqliteTool.operate_many(sql, [tuple(row) for index, row in df.iterrows()])
    sqliteTool.close_con()


def fetch_one_from_db(code: str):
    sqliteTool = SqliteTool()
    row = sqliteTool.query_one(f"select * from hk_stock where code = '{code}'")
    sqliteTool.close_con()
    return HKStock(code=row[0], name=row[1], price=row[2])


def fetch_all_from_db():
    sqliteTool = SqliteTool()
    rows = sqliteTool.query_many("select * from hk_stock")
    sqliteTool.close_con()
    return [HKStock(code=row[0], name=row[1], price=row[2]) for row in rows]


if __name__ == "__main__":
    # init_table()
    # init_hk_stock()
    # print(fetch_one_from_db('00700').name)
    print(fetch_all_from_db())
