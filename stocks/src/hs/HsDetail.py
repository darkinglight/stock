import datetime
from collections import namedtuple

from stocks.SqliteTool import SqliteTool
import akshare as ak
from hs.HsStock import HsStockRepository
import baostock as bs

HsDetail = namedtuple("HsDetail",
                      [
                          "code",
                          "name",
                          "price",
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
        self.sqlite_tool = SqliteTool(self.db_path)

    def init_table(self):
        """
        创建 hs_detail 数据表，如果表已存在则不做处理
        """
        create_tb_sql = (
            "CREATE TABLE IF NOT EXISTS hs_detail ("
            "code TEXT PRIMARY KEY, "
            "name TEXT, "
            "price REAL, "
            "pe REAL, "
            "pb REAL, "
            "bonus_rate REAL, "  # 分红率
            "roe_ttm REAL, "
            "earning_growth REAL, "
            "debt_ratio REAL, "
            "earning_growth_rush INTEGER "  # 增速是否上扬，方便判断困境反转
            ");"
        )
        # 创建数据表
        self.sqlite_tool.create_table(create_tb_sql)

    def drop_table(self):
        self.sqlite_tool.drop_table("drop table hs_detail;")

    def upsert_price(self, code: str, name: str, price: float, pe: float, pb: float):
        upsert_sql = (
            "INSERT INTO hs_detail (code, name, price, pe, pb) "
            "VALUES (?, ?, ?, ?, ?)"
            "ON CONFLICT(code) DO UPDATE SET name=excluded.name, price=excluded.price, pe=excluded.pe, pb=excluded.pb"
        )
        self.sqlite_tool.operate_one(upsert_sql, (code, name, price, pe, pb))

    def update_bonus(self, code: str, bonus_rate: float):
        sql = (
            "INSERT INTO hs_detail (code, bonus_rate) VALUES (?, ?)"
            "ON CONFLICT(code) DO UPDATE SET bonus_rate=excluded.bonus_rate"
        )
        self.sqlite_tool.operate_one(sql, (code, bonus_rate))

    def update_finance(self, code: str, roe_ttm: float, earning_growth: float, debt_ratio: float,
                       earning_growth_rush: int):
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
        self.sqlite_tool.operate_one(sql, (code, roe_ttm, earning_growth, debt_ratio, earning_growth_rush))

    def fetch_one_from_db(self, code: str):
        row = self.sqlite_tool.query_one(f"select * from hs_detail where code = '{code}'")
        if row is None:
            return None
        return HsDetail(*row)

    def find_one_by_name(self, name: str):
        row = self.sqlite_tool.query_one(f"select * from hs_detail where name = '{name}'")
        return HsDetail(*row) if row is not None else None

    def fetch_all_from_db(self):
        rows = self.sqlite_tool.query_many("select * from hs_detail")
        if rows is None:
            return []
        return [HsDetail(*item) for item in rows]

    #         item                value
    # 0         代码             SH600000
    # 1      52周最高                11.02
    # 2        流通股          29352178996
    # 3         跌停                 8.69
    # 4         最高                10.29
    # 5        流通值       299392225759.0
    # 6     最小交易单位                  100
    # 7         涨跌                 0.55
    # 8       每股收益                 1.54
    def refresh_price(self):
        hs_stock_repository = HsStockRepository()
        for stock in hs_stock_repository.fetch_all_valid_stocks()[0:10]:
            df = ak.stock_individual_spot_xq(symbol=stock.market + stock.code_number)
            price = df[df['item'] == '现价']['value'].iloc[0]
            pb = df[df['item'] == '市净率']['value'].iloc[0]
            pe = df[df['item'] == '市盈率(TTM)']['value'].iloc[0]
            self.upsert_price(stock.code, stock.name, price, pe, pb)

    def refresh_by_bao_stock(self):
        lg = bs.login()
        # 近10天的价格
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        date10ago = (datetime.datetime.now() - datetime.timedelta(days=10)).strftime("%Y-%m-%d")
        hs_stock_repository = HsStockRepository()
        for stock in hs_stock_repository.fetch_all_valid_stocks():
            rs = bs.query_history_k_data_plus(stock.code,
                                              "date,code,close,peTTM,pbMRQ",
                                              start_date=date10ago,
                                              end_date=date,
                                              frequency="d",
                                              adjustflag="3")
            if rs.error_code != '0':
                print(stock.code, rs.error_code, rs.error_msg)
            # 初始化变量存储最后一条记录
            last_item = None
            # 循环遍历所有记录，保留最后一条
            while rs.next():
                last_item = rs.get_row_data()
            # 处理最后一条记录
            if last_item:
                price = float(last_item[2])
                pe = float(last_item[3])
                pb = float(last_item[4])
                self.upsert_price(stock.code_number, stock.name, price, pe, pb)
        bs.logout()


if __name__ == "__main__":
    repository = HsDetailRepository("/Users/janet/Library/Application Support/com.example.stocks/finance.db")
    repository.drop_table()
    repository.init_table()
    # repository.upsert_price("002867", "凌霄泵业", 10, 10)
    # repository.update_bonus("002867", 10)
    # repository.update_finance("002867", 10, 10, 10, 1)
    # print(repository.fetch_one_from_db("002867"))
    repository.refresh_by_bao_stock()
