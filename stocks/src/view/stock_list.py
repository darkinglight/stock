from typing import List, Optional, Callable

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from models.stock import Stock


class StockListView(toga.Box):

    def __init__(self, stocks: Optional[List[Stock]] = None, on_select: Optional[Callable] = None, on_config_change: Optional[Callable] = None):
        self._on_select_handler = on_select
        self._on_config_change_handler = on_config_change
        self._stocks = stocks or []
        
        self._config = {
            'page_size': 20,
            'max_debt_ratio': 30.0,
            'min_pe': None,
            'max_pe': None,
            'min_pb': None,
            'max_pb': None,
            'min_roe': None,
            'max_roe': None,
            'min_bonus_rate': None,
            'max_bonus_rate': None,
            'sort_by': 'growth',
            'sort_order': 'desc'
        }
        
        super().__init__(style=Pack(flex=1, direction=COLUMN))

        self.table = toga.Table(
            headings=["代码", "名称", "PE", "PB", "分红率", "资产负债率", "ROE", "增长率"],
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
        self._stocks = stocks
        self.table.data = self._build_data(stocks)

    def show_config_dialog(self):
        dialog = toga.Window(title="列表配置")
        
        content_box = toga.Box(style=Pack(direction=COLUMN, margin=10))
        
        page_size_label = toga.Label("每页显示数量:", style=Pack(margin_bottom=5))
        self.page_size_input = toga.NumberInput(value=self._config['page_size'], style=Pack(margin_bottom=15))
        
        max_debt_label = toga.Label("最大资产负债率(%):", style=Pack(margin_bottom=5))
        self.max_debt_input = toga.NumberInput(value=self._config['max_debt_ratio'], style=Pack(margin_bottom=15))
        
        min_pe_label = toga.Label("最小市盈率:", style=Pack(margin_bottom=5))
        self.min_pe_input = toga.NumberInput(value=self._config['min_pe'] or 0, style=Pack(margin_bottom=15))
        
        max_pe_label = toga.Label("最大市盈率:", style=Pack(margin_bottom=5))
        self.max_pe_input = toga.NumberInput(value=self._config['max_pe'] or 100, style=Pack(margin_bottom=15))
        
        min_pb_label = toga.Label("最小市净率:", style=Pack(margin_bottom=5))
        self.min_pb_input = toga.NumberInput(value=self._config['min_pb'] or 0, style=Pack(margin_bottom=15))
        
        max_pb_label = toga.Label("最大市净率:", style=Pack(margin_bottom=5))
        self.max_pb_input = toga.NumberInput(value=self._config['max_pb'] or 10, style=Pack(margin_bottom=15))
        
        min_roe_label = toga.Label("最小ROE(%):", style=Pack(margin_bottom=5))
        self.min_roe_input = toga.NumberInput(value=self._config['min_roe'] or 0, style=Pack(margin_bottom=15))
        
        max_roe_label = toga.Label("最大ROE(%):", style=Pack(margin_bottom=5))
        self.max_roe_input = toga.NumberInput(value=self._config['max_roe'] or 100, style=Pack(margin_bottom=15))
        
        min_bonus_label = toga.Label("最小分红率(%):", style=Pack(margin_bottom=5))
        self.min_bonus_input = toga.NumberInput(value=self._config['min_bonus_rate'] or 0, style=Pack(margin_bottom=15))
        
        max_bonus_label = toga.Label("最大分红率(%):", style=Pack(margin_bottom=5))
        self.max_bonus_input = toga.NumberInput(value=self._config['max_bonus_rate'] or 100, style=Pack(margin_bottom=15))
        
        sort_by_label = toga.Label("排序字段:", style=Pack(margin_bottom=5))
        self.sort_by_selection = toga.Selection(
            items=['growth', 'pe', 'pb', 'roe', 'bonus_rate', 'assets_debt_ratio'],
            value=self._config['sort_by'],
            style=Pack(margin_bottom=15)
        )
        
        sort_order_label = toga.Label("排序顺序:", style=Pack(margin_bottom=5))
        self.sort_order_selection = toga.Selection(
            items=['desc', 'asc'],
            value=self._config['sort_order'],
            style=Pack(margin_bottom=20)
        )
        
        button_box = toga.Box(style=Pack(direction=ROW, margin_top=10))
        
        def on_save(widget):
            self._config['page_size'] = int(self.page_size_input.value)
            self._config['max_debt_ratio'] = float(self.max_debt_input.value)
            self._config['min_pe'] = float(self.min_pe_input.value) if self.min_pe_input.value > 0 else None
            self._config['max_pe'] = float(self.max_pe_input.value) if self.max_pe_input.value < 100 else None
            self._config['min_pb'] = float(self.min_pb_input.value) if self.min_pb_input.value > 0 else None
            self._config['max_pb'] = float(self.max_pb_input.value) if self.max_pb_input.value < 10 else None
            self._config['min_roe'] = float(self.min_roe_input.value) if self.min_roe_input.value > 0 else None
            self._config['max_roe'] = float(self.max_roe_input.value) if self.max_roe_input.value < 100 else None
            self._config['min_bonus_rate'] = float(self.min_bonus_input.value) if self.min_bonus_input.value > 0 else None
            self._config['max_bonus_rate'] = float(self.max_bonus_input.value) if self.max_bonus_input.value < 100 else None
            self._config['sort_by'] = self.sort_by_selection.value
            self._config['sort_order'] = self.sort_order_selection.value
            
            dialog.close()
            
            if self._on_config_change_handler:
                self._on_config_change_handler(self._config)
        
        def on_cancel(widget):
            dialog.close()
        
        save_button = toga.Button("保存", on_press=on_save, style=Pack(margin_right=10))
        cancel_button = toga.Button("取消", on_press=on_cancel)
        
        button_box.add(save_button)
        button_box.add(cancel_button)
        
        content_box.add(page_size_label)
        content_box.add(self.page_size_input)
        content_box.add(max_debt_label)
        content_box.add(self.max_debt_input)
        content_box.add(min_pe_label)
        content_box.add(self.min_pe_input)
        content_box.add(max_pe_label)
        content_box.add(self.max_pe_input)
        content_box.add(min_pb_label)
        content_box.add(self.min_pb_input)
        content_box.add(max_pb_label)
        content_box.add(self.max_pb_input)
        content_box.add(min_roe_label)
        content_box.add(self.min_roe_input)
        content_box.add(max_roe_label)
        content_box.add(self.max_roe_input)
        content_box.add(min_bonus_label)
        content_box.add(self.min_bonus_input)
        content_box.add(max_bonus_label)
        content_box.add(self.max_bonus_input)
        content_box.add(sort_by_label)
        content_box.add(self.sort_by_selection)
        content_box.add(sort_order_label)
        content_box.add(self.sort_order_selection)
        content_box.add(button_box)
        
        dialog.content = content_box
        dialog.show()

    def get_config(self):
        return self._config.copy()
