import json
import os
from pathlib import Path

import toga

from toga.style.pack import Pack

from stocks import hkstock


def init(path: Path):
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
    
    with open(cache_path, 'w') as f:
        json.dump(data, f)


def stock_list():
    rows = hkstock.fetch_all_from_db()
    # data = [("root%s" % i, "value %s" % i) for i in range(1, 100)]
    data = [(row.code, row.name) for row in rows]
    return toga.Table(headings=["code", "name"], data=data, style=Pack(flex=1))
