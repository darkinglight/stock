from typing import List, Optional, Callable

import toga
from toga.style import Pack
from toga.style.pack import COLUMN

from models.stock import Stock


class StockListView(toga.Box):

    def __init__(self, stocks: Optional[List[Stock]] = None, on_select: Optional[Callable] = None, on_config_change: Optional[Callable] = None):
        self._on_select_handler = on_select
        self._stocks = stocks or []
        
        super().__init__(style=Pack(flex=1, direction=COLUMN))

        self.table = toga.Table(
            headings=["ID", "代码", "名称", "PE", "PB", "分红率", "资产负债率", "ROE", "增长率"],
            data=self._build_data(self._stocks),
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
        for i, s in enumerate(stocks, 1):
            rows.append((
                str(i),
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
        self._stocks = stocks
        # 构建新的数据列表
        new_data = self._build_data(stocks)
        # 设置表格数据，Toga 会自动更新视图
        self.table.data = new_data