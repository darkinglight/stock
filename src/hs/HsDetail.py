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
        self.db_path = db_path

    def init_table(self):
        """
        创建 hs_detail 数据表，如果表已存在则不做处理
        """
        create_tb_sql = (
            "CREATE TABLE IF NOT EXISTS hs_detail ("
            "code TEXT PRIMARY KEY, "
            "name TEXT, "
            "pe REAL, "
            "pb REAL, "
            "bonus_rate REAL, "  # 分红率
            "roe_ttm REAL, "
            "earning_growth REAL, "
            "debt_ratio REAL, "
            "earning_growth_rush INTEGER "  # 增速是否上扬，方便判断困境反转
            ");"
        )
        sqlite_tool = SqliteTool(self.db_path)
        # 创建数据表
        sqlite_tool.create_table(create_tb_sql)
        sqlite_tool.close_con()

    def drop_table(self):
        sqlite_tool = SqliteTool(self.db_path)
        sqlite_tool.drop_table("drop table hs_detail;")
        sqlite_tool.close_con()

    def upsert_price(self, code: str, name: str, pe: float, pb: float):
        """
        如果指定 code 的记录存在则更新，不存在则插入
        """
        upsert_sql = (
            "INSERT INTO hs_detail (code, name, pe, pb) "
            "VALUES (?, ?, ?, ?)"
            "ON CONFLICT(code) DO UPDATE SET name=excluded.name, pe=excluded.pe, pb=excluded.pb"
        )
        sqlite_tool = SqliteTool(self.db_path)
        sqlite_tool.operate_one(upsert_sql, (code, name, pe, pb))
        sqlite_tool.close_con()

    def update_bonus(self, code: str, bonus_rate: float):
        sql = (
            "INSERT INTO hs_detail (code, bonus_rate) VALUES (?, ?)"
            "ON CONFLICT(code) DO UPDATE SET bonus_rate=excluded.bonus_rate"
        )
        sqlite_tool = SqliteTool(self.db_path)
        sqlite_tool.operate_one(sql, (code, bonus_rate))
        sqlite_tool.close_con()

    def update_finance(self, code: str, roe_ttm: float, earning_growth: float, debt_ratio: float, earning_growth_rush: int):
        sql = (
            "INSERT INTO hs_detail "
            "(code, roe_ttm, earning_growth, debt_ratio, earning_growth_rush) "
            "VALUES (?, ?, ?, ?, ?)"
            "ON CONFLICT(code) DO UPDATE SET "
            "roe_ttm=excluded.roe_ttm, "
            "earning_growth=excluded.earning_growth, "
            "debt_ratio=excluded.debt_ratio, "
            "earning_growth_rush=excluded.earning_growth_rush"
        )
        sqlite_tool = SqliteTool(self.db_path)
        sqlite_tool.operate_one(sql, (code, roe_ttm, earning_growth, debt_ratio, earning_growth_rush))
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
    # repository.init_table()
    repository.upsert_price("002867", "凌霄泵业", 10, 10)
    repository.update_bonus("002867", 10)
    repository.update_finance("002867", 10, 10, 10, 1)
    print(repository.fetch_one_from_db("002867"))
