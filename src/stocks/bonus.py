from collections import namedtuple

import akshare as ak

from stocks.SqliteTool import SqliteTool

HKBonus = namedtuple("HKBonus", ['code', 'report_date', 'detail', 'type'])


class HKBonusRepository:
    def __init__(self, db_path: str = "finance.db"):
        self.db_path = db_path

    def init_table(self):
        # 创建数据表info的SQL语句
        create_tb_sql = ("create table if not exists hk_bonus("
                         "code text,"
                         "report_date text,"
                         "detail text,"
                         "type text"
                         ");")
        sqlite_tool = SqliteTool(dbname=self.db_path)
        # 创建数据表
        sqlite_tool.create_table(create_tb_sql)
        sqlite_tool.close_con()

    def drop_table(self):
        sqlite_tool = SqliteTool(dbname=self.db_path)
        sqlite_tool.drop_table("drop table hk_bonus;")
        sqlite_tool.close_con()

    def init_hk_stock(self, code: str):
        # 获取数据
        df = ak.stock_hk_fhpx_detail_ths(symbol=code)
        df = df[["公告日期", "方案", "类型"]]
        df.insert(0, 'code', code)
        sql = f'insert into hk_bonus values(?, ?, ?, ?)'
        sqlite_tool = SqliteTool(dbname=self.db_path)
        sqlite_tool.operate_many(sql, [tuple(row) for index, row in df.iterrows()])
        sqlite_tool.close_con()

    def fetch_one_from_db(self, code: str):
        sqlite_tool = SqliteTool(dbname=self.db_path)
        row = sqlite_tool.query_one(f"select * from hk_bonus where code = '{code}'")
        sqlite_tool.close_con()
        return HKBonus(code=row[0], report_date=row[1], detail=row[2], type=row[3])

    def fetch_all_from_db(self):
        sqlite_tool = SqliteTool(dbname=self.db_path)
        rows = sqlite_tool.query_many("select * from hk_bonus")
        sqlite_tool.close_con()
        if rows is None:
            return []
        return [HKBonus(code=row[0], report_date=row[1], detail=row[2], type=row[3]) for row in rows]


if __name__ == "__main__":
    repository = HKBonusRepository()
    repository.init_table()
    repository.init_hk_stock("0700")
    print(repository.fetch_one_from_db("0700"))
