import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW


class StockConfigView(toga.Box):

    # 默认配置
    DEFAULT_CONFIG = {
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
        'min_roe_stability': None,
        'max_roe_stability': None,
        'min_roe_trend': None,
        'max_roe_trend': None,
        'sort_by': 'growth',
        'sort_order': 'desc'
    }

    def __init__(self, on_config_change=None, on_back=None, default_config=None):
        super().__init__(style=Pack(flex=1, direction=COLUMN))
        
        self._on_config_change_handler = on_config_change
        self._on_back_handler = on_back
        self._config = self.DEFAULT_CONFIG.copy()
        if default_config:
            self._config.update(default_config)
        
        self._create_ui()

    def _create_ui(self):
        # 创建内容容器
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
        
        min_roe_stability_label = toga.Label("最小ROE稳定性:", style=Pack(margin_bottom=5))
        self.min_roe_stability_input = toga.NumberInput(value=self._config['min_roe_stability'] or 0, style=Pack(margin_bottom=15))
        
        max_roe_stability_label = toga.Label("最大ROE稳定性:", style=Pack(margin_bottom=5))
        self.max_roe_stability_input = toga.NumberInput(value=self._config['max_roe_stability'] or 10, style=Pack(margin_bottom=15))
        
        min_roe_trend_label = toga.Label("最小ROE趋势:", style=Pack(margin_bottom=5))
        self.min_roe_trend_input = toga.NumberInput(value=self._config['min_roe_trend'] or 0, style=Pack(margin_bottom=15))
        
        max_roe_trend_label = toga.Label("最大ROE趋势:", style=Pack(margin_bottom=5))
        self.max_roe_trend_input = toga.NumberInput(value=self._config['max_roe_trend'] or 10, style=Pack(margin_bottom=15))
        
        sort_by_label = toga.Label("排序字段:", style=Pack(margin_bottom=5))
        self.sort_by_selection = toga.Selection(
            items=['growth', 'pe', 'pb', 'roe', 'bonus_rate', 'assets_debt_ratio', 'roe_stability', 'roe_trend', 'growth / pb', 'growth / pe'],
            value=self._config['sort_by'],
            style=Pack(margin_bottom=15)
        )
        
        sort_order_label = toga.Label("排序顺序:", style=Pack(margin_bottom=5))
        self.sort_order_selection = toga.Selection(
            items=['desc', 'asc'],
            value=self._config['sort_order'],
            style=Pack(margin_bottom=20)
        )
        
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
        content_box.add(min_roe_stability_label)
        content_box.add(self.min_roe_stability_input)
        content_box.add(max_roe_stability_label)
        content_box.add(self.max_roe_stability_input)
        content_box.add(min_roe_trend_label)
        content_box.add(self.min_roe_trend_input)
        content_box.add(max_roe_trend_label)
        content_box.add(self.max_roe_trend_input)
        content_box.add(sort_by_label)
        content_box.add(self.sort_by_selection)
        content_box.add(sort_order_label)
        content_box.add(self.sort_order_selection)
        
        # 创建滚动容器并添加内容
        scroll_container = toga.ScrollContainer(style=Pack(flex=1))
        scroll_container.content = content_box
        
        # 将滚动容器添加到主容器
        self.add(scroll_container)

    def _on_save(self, widget):
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
        self._config['min_roe_stability'] = float(self.min_roe_stability_input.value) if self.min_roe_stability_input.value > 0 else None
        self._config['max_roe_stability'] = float(self.max_roe_stability_input.value) if self.max_roe_stability_input.value < 10 else None
        self._config['min_roe_trend'] = float(self.min_roe_trend_input.value) if self.min_roe_trend_input.value > 0 else None
        self._config['max_roe_trend'] = float(self.max_roe_trend_input.value) if self.max_roe_trend_input.value < 10 else None
        self._config['sort_by'] = self.sort_by_selection.value
        self._config['sort_order'] = self.sort_order_selection.value
        
        if self._on_config_change_handler:
            self._on_config_change_handler(self._config)
        
        if self._on_back_handler:
            self._on_back_handler()

    def _on_cancel(self, widget):
        if self._on_back_handler:
            self._on_back_handler()

    def _on_back(self, widget):
        if self._on_back_handler:
            self._on_back_handler()

    def get_config(self):
        return self._config.copy()

    def set_config(self, config):
        self._config.update(config)