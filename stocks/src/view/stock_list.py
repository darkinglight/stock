from typing import List, Optional, Callable

import toga
from toga.style import Pack

from models.stock import Stock


class StockListView(toga.Box):

    def __init__(self, stocks: Optional[List[Stock]] = None, on_select: Optional[Callable] = None):
        self._on_select_handler = on_select
        super().__init__(style=Pack(flex=1))

        self.table = toga.Table(
            headings=["代码", "名称", "市场", "价格", "PE", "PB", "分红率", "每股净资产", "每股收益", "资产负债率", "ROE", "增长率"],
            data=self._build_data(stocks or []),
            on_select=self._on_select,
            style=Pack(flex=1),
        )
        self.add(self.table)

    def _build_data(self, stocks: List[Stock]) -> list:
        rows = []
        for s in stocks:
            rows.append((
                s.code,
                s.name or "",
                s.market or "",
                s.price if s.price is not None else "",
                s.pe if s.pe is not None else "",
                s.pb if s.pb is not None else "",
                s.bonus_rate if s.bonus_rate is not None else "",
                s.net_asset_per_share if s.net_asset_per_share is not None else "",
                s.basic_eps if s.basic_eps is not None else "",
                s.assets_debt_ratio if s.assets_debt_ratio is not None else "",
                s.roe if s.roe is not None else "",
                s.growth if s.growth is not None else "",
            ))
        return rows

    def _on_select(self, widget, row, **kwargs):
        if self._on_select_handler and row is not None:
            self._on_select_handler(row)

    def update_data(self, stocks: List[Stock]):
        """更新整个数据集"""
        self.table.data = self._build_data(stocks)

    def append_data(self, stocks: List[Stock]):
        """追加数据到现有数据集"""
        current_data = self.table.data
        new_data = self._build_data(stocks)
        self.table.data = current_data + new_data
