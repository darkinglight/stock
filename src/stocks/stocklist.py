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

def init_finance(path: Path):
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

