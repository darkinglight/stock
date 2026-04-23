from typing import List, Optional, Callable

import toga
from toga.style import Pack
from toga.style.pack import COLUMN

from models.stock import Stock


class HkStockListView(toga.Box):

    def __init__(self, stocks: Optional[List[Stock]] = None, on_select: Optional[Callable] = None):
        self._on_select_handler = on_select
        self._stocks = stocks or []
        
        super().__init__(style=Pack(flex=1, direction=COLUMN))

        self.table = toga.Table(
            headings=["ID", "代码", "名称", "价格"],
            accessors=["id", "code", "name", "price"],
            data=self._build_data(self._stocks),
            on_select=self._on_select,
            style=Pack(flex=1),
        )
        self.add(self.table)

    @staticmethod
    def _fmt(val):
        if val is None:
            return ""
        return f"{val:.2f}"

    def _build_data(self, stocks: List[Stock]) -> list:
        rows = []
        for i, s in enumerate(stocks, 1):
            rows.append((
                str(i),
                s.code,
                s.name or "",
                self._fmt(s.price),
            ))
        return rows

    def _on_select(self, widget, **kwargs):
        row = widget.selection
        if self._on_select_handler and row is not None:
            row_data = (
                getattr(row, 'id', ''),
                getattr(row, 'code', ''),
                getattr(row, 'name', ''),
                getattr(row, 'price', ''),
            )
            self._on_select_handler(row_data)

    def update_data(self, stocks: List[Stock]):
        self._stocks = stocks
        new_data = self._build_data(stocks)
        self.table.data = new_data