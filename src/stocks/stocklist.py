import json
import os
from pathlib import Path

import toga
import datetime

from toga.style.pack import Pack

from stocks import hkstock, hkfinancial


def init_stock(path: Path):
    data = dict()
    cache_path = os.path.join(path, "config_stock_list.json")
    if not os.path.exists(cache_path):
        os.makedirs(path, exist_ok=True)
        with open(cache_path, 'w') as f:
            json.dump(data, f)
    with open(cache_path, 'r') as f:
        data = json.load(f)
    if not data.get('init', False):
        hkstock.init_table()
        data['init'] = True
    # 根据时间更新数据
    today = datetime.date.today().strftime('%Y-%m-%d')
    pre_date = data.get('date', '')
    if today != pre_date:
        hkstock.init_hk_stock()
        data['date'] = today
    with open(cache_path, 'w') as f:
        json.dump(data, f)


async def init_finance(path: Path):
    data = dict()
    cache_path = os.path.join(path, "config_stock_list.json")
    with open(cache_path, 'r') as f:
        data = json.load(f)
    if not data.get('init_finance', False):
        hkfinancial.create_table()
        data['init_finance'] = True
    # 根据时间更新数据
    today = datetime.date.today().strftime('%Y-%m-%d')
    pre_date = data.get('date_finance', '')
    if today != pre_date:
        hkfinancial.refresh_all()
        data['date_finance'] = today
    with open(cache_path, 'w') as f:
        json.dump(data, f)


class Stocklist(toga.Box):
    def __init__(self, cache_path: Path, on_active):
        init_stock(cache_path)
        init_finance(cache_path)
        super().__init__(children=[self.stock_list(on_active)])

    def stock_list(self, on_active):
        rows = hkstock.fetch_all_from_db()
        # data = [("root%s" % i, "value %s" % i) for i in range(1, 100)]
        data = []
        for row in rows:
            finance_item = hkfinancial.fetch_last_year_report(row.code)
            data.append((row.code, row.name, finance_item.EPS_TTM))
        data.sort(key=lambda a: a[2])
        return toga.Table(headings=["code", "name", "eps"],
                          data=data,
                          on_select=on_active,
                          style=Pack(flex=1))
