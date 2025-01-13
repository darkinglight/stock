from pathlib import Path

import toga

from toga.style.pack import Pack

from stocks import hkfinancial
from stocks.hkstock import HkStockRepository


class Stocklist(toga.Box):
    cache = dict()

    def __init__(self, data_path: Path, on_active):
        # self.cache_path = os.path.join(cache_path, "config_stock_list.json")
        self.db_file = data_path
        # self.init_cache(path=cache_path)
        # self.init_stock()
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


    # def init_stock(self):
    #     with open(self.cache_path, 'r') as f:
    #         self.cache = json.load(f)
    #     if not self.cache.get('init', False):
    #         self.cache['init'] = True
    #         with open(self.cache_path, 'w') as f:
    #             json.dump(self.cache, f)
