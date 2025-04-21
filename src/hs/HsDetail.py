from collections import namedtuple

from stocks.SqliteTool import SqliteTool

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
        self.code_set = None
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
        sqlite_tool.drop_table("drop table hs_detail;")
        sqlite_tool.close_con()

    def get_code_set(self) -> set[str]:
        if self.code_set is None:
            sqlite_tool = SqliteTool(self.db_path)
            rows = sqlite_tool.query_many("select code from hs_detail")
            sqlite_tool.close_con()
            self.code_set = set([item[0] for item in rows])
        return self.code_set

    def init_code(self, code: str):
        if code in self.get_code_set():
            return
        sqlite_tool = SqliteTool(self.db_path)
        sqlite_tool.operate_one("insert into hs_detail(code) values(?)", (code,))
        sqlite_tool.close_con()
        self.code_set.add(code)

    def update_price(self, code: str, name: str, pe: float, pb: float):
        self.init_code(code)
        sqlite_tool = SqliteTool(self.db_path)
        sqlite_tool.operate_one("update hs_detail set name = ?, pe = ?, pb = ? where code = ?", (name, pe, pb, code))
        sqlite_tool.close_con()

    def update_bonus(self, code: str, bonus_rate: float):
        self.init_code(code)
        sqlite_tool = SqliteTool(self.db_path)
        sqlite_tool.operate_one("update hs_detail set bonus_rate =? where code =?", (bonus_rate, code))
        sqlite_tool.close_con()

    def update_finance(self, code: str, roe_ttm: float, earning_growth: float, debt_ratio: float, earning_growth_rush: bool):
        self.init_code(code)
        sqlite_tool = SqliteTool(self.db_path)
        sqlite_tool.operate_one("update hs_detail set roe_ttm =?, earning_growth =?, debt_ratio =?, earning_growth_rush =? where code =?", (roe_ttm, earning_growth, debt_ratio, earning_growth_rush, code))
        sqlite_tool.close_con()

    def fetch_one_from_db(self, code: str):
        sqlite_tool = SqliteTool(self.db_path)
        row = sqlite_tool.query_one(f"select * from hs_detail where code = '{code}'")
        sqlite_tool.close_con()
        return HsDetail(*row)

    def find_one_by_name(self, name: str):
        sqlite_tool = SqliteTool(self.db_path)
        row = sqlite_tool.query_one(f"select * from hs_detail where name = '{name}'")
        sqlite_tool.close_con()
        return HsDetail(*row)

    def fetch_all_from_db(self):
        sqlite_tool = SqliteTool(self.db_path)
        rows = sqlite_tool.query_many("select * from hs_detail")
        sqlite_tool.close_con()
        if rows is None:
            return []
        return [HsDetail(*item) for item in rows]


if __name__ == "__main__":
    repository = HsDetailRepository()
    # repository.drop_table()
    repository.init_table()
    repository.update_price("002867", "凌霄泵业", 10, 10)
    repository.update_bonus("002867", 10)
    repository.update_finance("002867", 10, 10, 10, True)
    print(repository.fetch_one_from_db("002867"))
