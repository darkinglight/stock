from collections import namedtuple

import akshare as ak

from SqliteTool import SqliteTool

# 创建对象
sqliteTool = SqliteTool()

HKStock = namedtuple("HKStock", ['code', 'name', 'price'])


def init_table():
    # 创建数据表info的SQL语句
    create_tb_sql = ("create table if not exists hk_stock("
                     "code text primary key,"
                     "name text,"
                     "price float"
                     ");")
    # 删除表
    sqliteTool.drop_table("drop table hk_stock;")
    # 创建数据表
    sqliteTool.create_table(create_tb_sql)


def init_hk_stock():
    # 获取数据
    df = ak.stock_hk_ggt_components_em()
    df = df[["代码", "名称", "最新价"]]
    sql = 'insert into hk_stock values(?,?,?)'
    sqliteTool.operate_many(sql, [tuple(row) for index, row in df.iterrows()])


def fetch_one_from_db(code: str):
    row = sqliteTool.query_one(f"select * from hk_stock where code = '{code}'")
    return HKStock(code=row[0], name=row[1], price=row[2])


def fetch_all_from_db():
    rows = sqliteTool.query_many("select * from hk_stock")
    return [HKStock(code=row[0], name=row[1], price=row[2]) for row in rows]


if __name__ == "__main__":
    # init_table()
    # init_hk_stock()
    print(fetch_one_from_db('00700').name)
    print(fetch_all_from_db())
