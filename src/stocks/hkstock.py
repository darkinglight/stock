import datetime
from collections import namedtuple

import akshare as ak

from stocks.SqliteTool import SqliteTool

HKStock = namedtuple("HKStock", ['code', 'name', 'price', 'update_at'])


class HkStockRepository:

    def __init__(self, data_path='finance.db'):
        self.data_path = data_path

    def init_table(self):
        # 创建数据表info的SQL语句
        create_tb_sql = ("create table if not exists hk_stock("
                         "code text primary key,"
                         "name text,"
                         "price float,"
                         "update_at text"
                         ");")
        sqlite_tool = SqliteTool(self.data_path)
        # 创建数据表
        sqlite_tool.create_table(create_tb_sql)
        sqlite_tool.close_con()

    def drop_table(self):
        sqlite_tool = SqliteTool(self.data_path)
        sqlite_tool.drop_table("drop table hk_stock;")
        sqlite_tool.close_con()

    def get_latest_update_time(self):
        # 查询最新的更新时间
        sqlite_tool = SqliteTool(self.data_path)
        row = sqlite_tool.query_one("select max(update_at) from hk_stock")
        sqlite_tool.close_con()
        if row[0]:
            return datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
        else:
            return datetime.datetime.min

    def init_hk_stock(self):
        # 1. 无记录,时间为min < 当天16:30 2.更新日期 < 当天16:30
        latest_update_time = self.get_latest_update_time()
        # 计算时间差
        time_diff = datetime.datetime.now() - latest_update_time
        # 计算当天 16:30 的时间
        today_1630 = datetime.datetime.now().replace(hour=16, minute=30, second=0, microsecond=0)
        if latest_update_time < today_1630 and time_diff.total_seconds() > 3600:
            # 获取数据
            df = ak.stock_hk_ggt_components_em()
            df = df[["代码", "名称", "最新价"]]
            df['update_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            sql = 'insert into hk_stock values(?,?,?,?)'
            sqlite_tool = SqliteTool(self.data_path)
            sqlite_tool.operate_many(sql, [tuple(row) for index, row in df.iterrows()])
            sqlite_tool.close_con()

    def fetch_one_from_db(self, code: str):
        sqlite_tool = SqliteTool(self.data_path)
        row = sqlite_tool.query_one(f"select * from hk_stock where code = '{code}'")
        sqlite_tool.close_con()
        return HKStock(code=row[0], name=row[1], price=row[2], update_at=row[3])

    def fetch_all_from_db(self) -> list[HKStock]:
        sqlite_tool = SqliteTool(self.data_path)
        rows = sqlite_tool.query_many("select * from hk_stock")
        sqlite_tool.close_con()
        if rows is None:
            return []
        return [HKStock(code=row[0], name=row[1], price=row[2], update_at=[3]) for row in rows]


if __name__ == "__main__":
    repository = HkStockRepository()
    repository.init_table()
    repository.init_hk_stock()
    print(repository.fetch_one_from_db('00700').name)
    print(HkStockRepository().fetch_all_from_db())
