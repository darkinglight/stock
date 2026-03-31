from collections import namedtuple
from datetime import datetime

import akshare as ak
from stocks.SqliteTool import SqliteTool

Bond = namedtuple("Bond", [
    "bond_code",
    "bond_name",
    "bond_price",
    "stock_code",
    "stock_over_percent",
    "bond_over_percent",
    "stock_roe",
    "stock_debt_ratio"
])


class BondRepository:
    def __init__(self, db_path: str = "finance.db"):
        self.db_path = db_path

    def init_table(self):
        # %s#\(.*\)\s\(.*\)\s\(.*\)#"\1" \2,#
        sql = """
        create table if not exists bond(
            "序号" int32,
            "转债代码" text,
            "转债名称" text,
            "转债最新价" text,
            "转债涨跌幅" text,
            "正股代码" text,
            "正股名称" text,
            "正股最新价" text,
            "正股涨跌幅" text,
            "转股价" text,
            "转股价值" text,
            "转股溢价率" text,
            "纯债溢价率" text,
            "回售触发价" text,
            "强赎触发价" text,
            "到期赎回价" text,
            "纯债价值" float64,
            "开始转股日" text,
            "上市日期" text,
            "申购日期" text,
            update_at text -- 更新时间
        ); 
        """
        sqlite_tool = SqliteTool(self.db_path)
        # 创建数据表
        sqlite_tool.create_table(sql)
        sqlite_tool.close_con()

    def drop_table(self):
        sqlite_tool = SqliteTool(self.db_path)
        sqlite_tool.drop_table("drop table bond;")
        sqlite_tool.close_con()

    def __fetch_from_api(self):
        df = ak.bond_cov_comparison()
        return df

    def refresh(self):
        latest_update_time = self.get_latest_update_time()
        # 计算时间差
        time_diff = datetime.now() - latest_update_time
        if time_diff.total_seconds() > 3600 * 24:
            rows = self.__fetch_from_api()
            rows['update_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # 根据字典的键动态生成插入语句
            sql = ('INSERT INTO bond ("' + '", "'.join(rows.columns.values) +
                   '") VALUES (' + ', '.join(['?'] * rows.shape[1]) + ')')
            # 执行批量插入操作
            sqlite_tool = SqliteTool(self.db_path)
            sqlite_tool.delete_record(f"delete from bond")
            sqlite_tool.operate_many(sql, [tuple(row) for index, row in rows.iterrows()])
            sqlite_tool.close_con()

    def get_latest_update_time(self):
        # 查询最新的更新时间
        sqlite_tool = SqliteTool(self.db_path)
        row = sqlite_tool.query_one(f"select max(update_at) from bond")
        sqlite_tool.close_con()
        if row[0]:
            return datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
        else:
            return datetime.min

    def fetch_all_from_db(self):
        sqlite_tool = SqliteTool(dbname=self.db_path)
        rows = sqlite_tool.query_many("select * from bond")
        sqlite_tool.close_con()
        if rows is None:
            return []
        return [Bond(bond_code=row[1], bond_name=row[2], bond_price=row[3], stock_code=row[5],
                     stock_over_percent=row[11], bond_over_percent=row[12],
                     stock_roe=1, stock_debt_ratio=1) for row in rows]

if __name__ == "__main__":
    repository = BondRepository()
    repository.init_table()
    repository.refresh()
