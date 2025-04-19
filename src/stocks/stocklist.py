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
        finances = hkfinancial.HkFinanceRepository(self.db_file).list_last_year_report()
        rows = HkStockRepository(self.db_file).fetch_all_from_db()
        # data = [("root%s" % i, "value %s" % i) for i in range(1, 100)]
        data = []
        for row in rows:
            finance_item = None
            for finance_row in finances:
                if finance_row.SECURITY_CODE == row.code:
                    finance_item = finance_row
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

