from pathlib import Path

import toga

from toga.style.pack import Pack

from stocks import hkfinancial
from stocks.hkstock import HkStockRepository


class Stocklist(toga.Box):
    cache = dict()

    def __init__(self, data_path: Path, on_active):
        self.db_file = data_path
        super().__init__(children=[self.stock_list(on_active)])

    def stock_list(self, on_active):
        # 获取财务数据
        finances = hkfinancial.HkFinanceRepository(self.db_file).list_last_year_report()
        # 将财务数据存储在字典中，以股票代码作为键
        finance_dict = {finance_row.SECURITY_CODE: finance_row for finance_row in finances}

        # 获取所有股票记录
        rows = HkStockRepository(self.db_file).fetch_all_from_db()
        data = []

        for row in rows:
            finance_item = finance_dict.get(row.code)
            if finance_item is None:
                print(f"{row.code} miss financial data")
                continue
            if (0 < finance_item.EPS_TTM < 30
                    and 0 < finance_item.ROE_YEARLY < 50
                    and finance_item.DEBT_ASSET_RATIO < 60):
                data.append((row.code,
                             row.name,
                             round(row.price / finance_item.BPS, 2),
                             round(row.price / finance_item.EPS_TTM, 2),
                             round(finance_item.ROE_YEARLY, 2),
                             round(finance_item.DEBT_ASSET_RATIO, 2)))
        data.sort(key=lambda a: a[3] / a[4])
        return toga.Table(headings=["code", "name", "pb", "pe", "年化净资产收益率(%)", "资产负债率(%)"],
                          data=data,
                          on_select=on_active,
                          style=Pack(flex=1))

