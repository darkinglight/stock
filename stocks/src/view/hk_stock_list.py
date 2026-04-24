from typing import List, Optional, Callable

import toga
from toga.style import Pack
from toga.style.pack import COLUMN

from models.stock import Stock


class HkStockListView(toga.Box):

    def __init__(self, stocks: Optional[List[Stock]] = None, on_select: Optional[Callable] = None, on_config_change: Optional[Callable] = None):
        self._on_select_handler = on_select
        self._on_config_change_handler = on_config_change
        self._stocks = stocks or []
        
        super().__init__(style=Pack(flex=1, direction=COLUMN))

        self.table = toga.Table(
            headings=["ID", "代码", "名称", "价格", "PE", "PB", "每股净资产", "每股收益", "资产负债率", "ROE"],
            accessors=["id", "code", "name", "price", "pe", "pb", "net_asset_per_share", "basic_eps", "assets_debt_ratio", "roe"],
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
                self._fmt(s.pe),
                self._fmt(s.pb),
                self._fmt(s.net_asset_per_share),
                self._fmt(s.basic_eps),
                self._fmt(s.assets_debt_ratio),
                self._fmt(s.roe),
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
                getattr(row, 'pe', ''),
                getattr(row, 'pb', ''),
                getattr(row, 'net_asset_per_share', ''),
                getattr(row, 'basic_eps', ''),
                getattr(row, 'assets_debt_ratio', ''),
                getattr(row, 'roe', ''),
            )
            self._on_select_handler(row_data)

    def update_data(self, stocks: List[Stock]):
        self._stocks = stocks
        new_data = self._build_data(stocks)
        self.table.data = new_data