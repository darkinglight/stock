from collections import namedtuple

from stocks.SqliteTool import SqliteTool
import akshare as ak

HsDetail = namedtuple("HsDetail",
                      [
                          "code",
                          "name",
                          "pe",
                          "pb",
                          "bonus_rate",  # 分红率
                          "roe_ttm",
                          "earning_growth",
                          "debt_ratio",
                          "earning_growth_rush",  # 增速是否上扬，方便判断困境反转
                      ])


class HsDetailRepository:

    def __init__(self, db_path: str = "finance.db"):
        self.db_path = db_path

    def init_table(self):
        # 创建数据表info的SQL语句
        create_tb_sql = ("create table if not exists hs_detail("
                         "code text primary key,"
                         "name text,"
                         "pe float64,"
                         "pb float64,"
                         "bonus_rate float64,"  # 分红率
                         "roe_ttm float64,"
                         "earning_growth float64,"
                         "debt_ratio float64,"
                         "earning_growth_rush boolean"  # 增速是否上扬，方便判断困境反转
                         ");")
        sqlite_tool = SqliteTool(self.db_path)
        # 创建数据表
        sqlite_tool.create_table(create_tb_sql)
        sqlite_tool.close_con()

    def drop_table(self):
        sqlite_tool = SqliteTool(self.db_path)
        sqlite_tool.drop_table("drop table hs_stock;")
        sqlite_tool.close_con()

    def update_price(self, code: str, name: str, pe: float, pb: float):
        sqlite_tool = SqliteTool(self.db_path)
        sqlite_tool.operate_one(f"update hs_stock set price = {price} where code = '{code}'")
        sqlite_tool.close_con()


    def fetch_one_from_db(self, code: str):
        sqlite_tool = SqliteTool(self.db_path)
        row = sqlite_tool.query_one(f"select * from hs_stock where code = '{code}'")
        sqlite_tool.close_con()
        return HsDetail(*row)

    def find_one_by_name(self, name: str):
        sqlite_tool = SqliteTool(self.db_path)
        row = sqlite_tool.query_one(f"select * from hs_stock where name = '{name}'")
        sqlite_tool.close_con()
        return HsDetail(*row)

    def fetch_all_from_db(self):
        sqlite_tool = SqliteTool(self.db_path)
        rows = sqlite_tool.query_many("select * from hs_stock")
        sqlite_tool.close_con()
        if rows is None:
            return []
        return [HsDetail(*item) for item in rows]


if __name__ == "__main__":
    repository = HsDetailRepository()
    # repository.init_table()
    # repository.init_hs_stock()
    # for row in repository.fetch_all_from_db():
    #     print(row.code, row.name)
    print(repository.fetch_one_from_db("002867"))
    print(repository.find_one_by_name("凌霄泵业"))
