from collections import namedtuple
from datetime import datetime
from pathlib import Path

import akshare as ak
import toga
from toga.style import Pack

from hs.HsDetail import HsDetailRepository
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


class BondBox(toga.Box):
    def __init__(self, data_path: Path, on_active):
        self.db_file = data_path
        super().__init__(children=[self.stock_list(on_active)])

    def stock_list(self, on_active):
        bond_repository = BondRepository(self.db_file)
        rows = bond_repository.fetch_all_from_db()
        hs_detail_repository = HsDetailRepository(self.db_file)
        box_data = []
        for row in rows:
            stock_detail = hs_detail_repository.fetch_one_from_db(row.stock_code)
            # 检查 bonus_rate 和 debt_ratio 是否为 None，若为 None 则赋予默认值
            if row.bond_price > 150:
                continue
            box_data.append((
                row.bond_code,
                row.bond_name,
                row.bond_price,
                row.bond_over_percent,
                row.stock_over_percent
            ))
        box_data.sort(reverse=False, key=lambda a: a[2])
        return toga.Table(headings=["转债代码", "转债名称", "转债最新价", "纯债溢价率", "转股溢价率"],
                          data=box_data,
                          on_select=on_active,
                          style=Pack(flex=1))


if __name__ == "__main__":
    repository = BondRepository()
    repository.init_table()
    repository.refresh()
