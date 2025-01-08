import json
import os
from pathlib import Path

import toga

from toga.style.pack import Pack

from stocks import hkstock, hkfinancial


def stock_list(on_active):
    finances = hkfinancial.list_last_year_report()
    rows = hkstock.fetch_all_from_db()
    # data = [("root%s" % i, "value %s" % i) for i in range(1, 100)]
    data = []
    for row in rows:
        finance_item = None
        for finance_row in finances:
            if finance_row.SECURITY_CODE == row.code:
                finance_item = finance_row
        data.append((row.code, row.name, -1000 if finance_item is None else finance_item.EPS_TTM))
    data.sort(key=lambda a: a[2])
    return toga.Table(headings=["code", "name", "eps"],
                      data=data,
                      on_select=on_active,
                      style=Pack(flex=1))


class Stocklist(toga.Box):
    cache = dict()

    def __init__(self, cache_path: Path, on_active):
        self.cache_path = os.path.join(cache_path, "config_stock_list.json")
        self.init_cache(path=cache_path)
        super().__init__(children=[stock_list(on_active)])

    def init_cache(self, path: Path):
        if not os.path.exists(self.cache_path):
            os.makedirs(path, exist_ok=True)
            with open(self.cache_path, 'w') as f:
                json.dump(self.cache, f)
        with open(self.cache_path, 'r') as f:
            self.cache = json.load(f)

    def init_stock(self):
        if not self.cache.get('init', False):
            hkstock.init_table()
            hkfinancial.create_table()
            self.cache['init'] = True
            with open(self.cache_path, 'w') as f:
                json.dump(self.cache, f)


