from typing import List, Optional, Callable

import toga
from toga.style import Pack
from toga.style.pack import COLUMN

from models.stock import Stock


class StockListView(toga.Box):

    def __init__(self, stocks: Optional[List[Stock]] = None, on_select: Optional[Callable] = None):
        self._on_select_handler = on_select
        super().__init__(style=Pack(flex=1, direction=COLUMN))

        self.table = toga.Table(
            headings=["代码", "名称", "PE", "PB", "分红率", "资产负债率", "ROE", "增长率"],
            data=self._build_data(stocks or []),
            on_select=self._on_select,
            style=Pack(flex=1),
        )
        self.add(self.table)

    @staticmethod
    def _fmt(val):
        if val is None:
            return ""
        return f"{val:.1f}"

    def _build_data(self, stocks: List[Stock]) -> list:
        rows = []
        for s in stocks:
            rows.append((
                s.code,
                s.name or "",
                self._fmt(s.pe),
                self._fmt(s.pb),
                self._fmt(s.bonus_rate),
                self._fmt(s.assets_debt_ratio),
                self._fmt(s.roe),
                self._fmt(s.growth),
            ))
        return rows

    def _on_select(self, widget, row, **kwargs):
        if self._on_select_handler and row is not None:
            self._on_select_handler(row)

    def update_data(self, stocks: List[Stock]):
        """更新整个数据集"""
        self.table.data = self._build_data(stocks)
