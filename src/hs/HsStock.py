from collections import namedtuple

import akshare as ak
import baostock as bs
from stocks.SqliteTool import SqliteTool

HSStock = namedtuple("HSStock", [
    'code',
    'market',
    'code_number',
    'name',
    'type',
    'status'
])


class HsStockRepository:

    def __init__(self, db_path: str = "finance.db"):
        self.sqlite_tool = SqliteTool(db_path)

    def init_table(self):
        # 创建数据表info的SQL语句
        create_tb_sql = ("create table if not exists hs_stock("
                         "code TEXT primary key,"
                         "market TEXT,"
                         "code_number TEXT,"
                         "name TEXT,"
                         "type INTEGER,"
                         "status INTEGER"
                         ");")
        # 创建数据表
        self.sqlite_tool.create_table(create_tb_sql)

    def drop_table(self):
        self.sqlite_tool.drop_table("drop table if exists hs_stock;")

    def init_hs_stock(self):
        df = ak.stock_zh_a_spot()
        sql = 'insert into hs_stock (code, name) values(?,?)'
        self.sqlite_tool.operate_many(sql, [tuple(row) for index, row in df.iterrows()])

    def init_bao_stock(self):
        rs = bs.query_all_stock(day="2025-11-03")
        if rs.error_code != '0':
            print('query_all_stock respond error_code:' + rs.error_code)
            print('query_all_stock respond  error_msg:' + rs.error_msg)
            return
        # 新增：创建数据列表用于批量插入
        data_list = []
        while (rs.error_code == '0') & rs.next():
            item = rs.get_row_data()
            code = item[0]  # 原始带市场标识的完整代码（如"sh.000003"）
            market, code_number = code.split('.')  # 按.拆分市场标识和证券代码
            data_list.append((code, market, code_number, item[2]))
        # 批量插入所有数据
        if data_list:
            self.sqlite_tool.operate_many('insert into hs_stock '
                                          '(code, market, code_number, name) values(?,?,?,?)', data_list)

    # # code	证券代码
    # # code_name	证券名称
    # # ipoDate	上市日期
    # # outDate	退市日期
    # # type	证券类型，其中1：股票，2：指数，3：其它，4：可转债，5：ETF
    # # status	上市状态，其中1：上市，0：退市
    def update_bao_stock_base_info(self, code: str):
        rs = bs.query_stock_basic(code=code)
        if rs.error_code != '0':
            print("get base info error: ", code, rs.error_code, rs.error_msg)
            return
        while rs.next():
            base_data = rs.get_row_data()
            # 根据注释提取type(索引4)和status(索引5)
            type_val = base_data[4]
            status_val = base_data[5]
            # 更新对应code的记录
            sql = "UPDATE hs_stock SET type = ?, status = ? WHERE code = ?"
            self.sqlite_tool.operate_one(sql, (type_val, status_val, code))

    # 更新所有股票的基础信息
    def update_all_bao_stock_base_info(self):
        rows = self.sqlite_tool.query_many("select code from hs_stock")
        if rows is None:
            return
        for row in rows:
            self.update_bao_stock_base_info(row[0])

    def fetch_one_from_db(self, code: str):
        row = self.sqlite_tool.query_one(f"select * from hs_stock where code = '{code}'")
        if row is None:
            return None
        return HSStock(code=row[0], market=row[1], code_number=row[2],
                       name=row[3], type=row[4], status=row[5])

    def find_one_by_name(self, name: str):
        row = self.sqlite_tool.query_one(f"select * from hs_stock where name = '{name}'")
        if row is None:
            return None
        return HSStock(*row)

    def fetch_all_from_db(self):
        rows = self.sqlite_tool.query_many("select code, market, code_number, name, "
                                           "type, status from hs_stock")
        if rows is None:
            return []
        return [HSStock(code=item[0], market=item[1], code_number=item[2],
                        name=item[3], type=item[4], status=item[5]) for item in rows]

    def fetch_all_valid_stocks(self):
        rows = self.sqlite_tool.query_many("select code, market, code_number, name "
                                           "from hs_stock where type = 1 and status = 1")
        if rows is None:
            return []
        return [HSStock(code=item[0], market=item[1], code_number=item[2],
                        name=item[3], type=1, status=1) for item in rows]


if __name__ == "__main__":
    # lg = bs.login()
    # if lg.error_code != '0':
    #     print('login respond error_code:' + lg.error_code)
    #     print('login respond  error_msg:' + lg.error_msg)
    repository = HsStockRepository("/Users/janet/Library/Application Support/com.example.stocks/finance.db")
    # repository = HsStockRepository()
    # repository.drop_table()
    # repository.init_table()
    # repository.init_bao_stock()
    # repository.update_all_bao_stock_base_info()
    # bs.logout()
    print(repository.fetch_one_from_db("sh.600054"))
    print(repository.find_one_by_name("凌霄泵业"))
    # 输出前10条有效股票
    for stock in repository.fetch_all_valid_stocks()[:10]:
        print(stock)
