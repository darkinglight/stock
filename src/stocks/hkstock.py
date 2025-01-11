from collections import namedtuple

import akshare as ak

from stocks.SqliteTool import SqliteTool

HKStock = namedtuple("HKStock", ['code', 'name', 'price'])


class HkStockRepository:

    def __init__(self, data_path='finance.db'):
        self.data_path = data_path

    def init_table(self):
        # 创建数据表info的SQL语句
        create_tb_sql = ("create table if not exists hk_stock("
                         "code text primary key,"
                         "name text,"
                         "price float"
                         ");")
        sqlite_tool = SqliteTool(self.data_path)
        # 创建数据表
        sqlite_tool.create_table(create_tb_sql)
        sqlite_tool.close_con()

    def drop_table(self):
        sqlite_tool = SqliteTool(self.data_path)
        sqlite_tool.drop_table("drop table hk_stock;")
        sqlite_tool.close_con()

    def init_hk_stock(self):
        # 获取数据
        df = ak.stock_hk_ggt_components_em()
        df = df[["代码", "名称", "最新价"]]
        sql = 'insert into hk_stock values(?,?,?)'
        sqlite_tool = SqliteTool(self.data_path)
        sqlite_tool.operate_many(sql, [tuple(row) for index, row in df.iterrows()])
        sqlite_tool.close_con()

    def fetch_one_from_db(self, code: str):
        sqlite_tool = SqliteTool(self.data_path)
        row = sqlite_tool.query_one(f"select * from hk_stock where code = '{code}'")
        sqlite_tool.close_con()
        return HKStock(code=row[0], name=row[1], price=row[2])

    def fetch_all_from_db(self):
        sqlite_tool = SqliteTool(self.data_path)
        rows = sqlite_tool.query_many("select * from hk_stock")
        sqlite_tool.close_con()
        if rows is None:
            return []
        return [HKStock(code=row[0], name=row[1], price=row[2]) for row in rows]


if __name__ == "__main__":
    # init_table()
    # init_hk_stock()
    # print(fetch_one_from_db('00700').name)
    print(HkStockRepository().fetch_all_from_db())
