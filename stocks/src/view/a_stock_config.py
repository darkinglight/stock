import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW


class StockConfigView(toga.Box):

    # 默认配置
    DEFAULT_CONFIG = {
        'page_size': 20,
        'max_debt_ratio': 30.0,
        'min_pe': 0,
        'max_pe': 100,
        'min_pb': 0,
        'max_pb': 10,
        'min_roe': 0,
        'max_roe': 100,
        'min_bonus_rate': 0,
        'max_bonus_rate': 100,
        'min_roe_stability': 0,
        'max_roe_stability': 100,
        'min_roe_trend': -100,
        'max_roe_trend': 100,
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
        
        # 每页显示数量
        page_size_label = toga.Label("每页显示数量:", style=Pack(margin_bottom=5))
        self.page_size_input = toga.NumberInput(value=self._config['page_size'] or self.DEFAULT_CONFIG['page_size'], style=Pack(margin_bottom=15))
        content_box.add(page_size_label)
        content_box.add(self.page_size_input)
        
        # 最大资产负债率
        max_debt_label = toga.Label("最大资产负债率(%):", style=Pack(margin_bottom=5))
        self.max_debt_input = toga.NumberInput(value=self._config['max_debt_ratio'] or self.DEFAULT_CONFIG['max_debt_ratio'], style=Pack(margin_bottom=15))
        content_box.add(max_debt_label)
        content_box.add(self.max_debt_input)
        
        # 市盈率范围
        pe_label = toga.Label("市盈率范围:", style=Pack(margin_bottom=5))
        pe_box = toga.Box(style=Pack(direction=ROW, margin_bottom=15, align_items="center"))
        self.min_pe_input = toga.NumberInput(value=self._config['min_pe'] or self.DEFAULT_CONFIG['min_pe'], style=Pack(width=80))
        pe_box.add(self.min_pe_input)
        pe_box.add(toga.Label(" < ", style=Pack(margin_left=5, margin_right=5)))
        pe_box.add(toga.Label("PE", style=Pack(margin_right=5)))
        pe_box.add(toga.Label(" < ", style=Pack(margin_right=5)))
        self.max_pe_input = toga.NumberInput(value=self._config['max_pe'] or self.DEFAULT_CONFIG['max_pe'], style=Pack(width=80))
        pe_box.add(self.max_pe_input)
        content_box.add(pe_label)
        content_box.add(pe_box)
        
        # 市净率范围
        pb_label = toga.Label("市净率范围:", style=Pack(margin_bottom=5))
        pb_box = toga.Box(style=Pack(direction=ROW, margin_bottom=15, align_items="center"))
        self.min_pb_input = toga.NumberInput(value=self._config['min_pb'] or self.DEFAULT_CONFIG['min_pb'], style=Pack(width=80))
        pb_box.add(self.min_pb_input)
        pb_box.add(toga.Label(" < ", style=Pack(margin_left=5, margin_right=5)))
        pb_box.add(toga.Label("PB", style=Pack(margin_right=5)))
        pb_box.add(toga.Label(" < ", style=Pack(margin_right=5)))
        self.max_pb_input = toga.NumberInput(value=self._config['max_pb'] or self.DEFAULT_CONFIG['max_pb'], style=Pack(width=80))
        pb_box.add(self.max_pb_input)
        content_box.add(pb_label)
        content_box.add(pb_box)
        
        # ROE范围
        roe_label = toga.Label("ROE范围(%):", style=Pack(margin_bottom=5))
        roe_box = toga.Box(style=Pack(direction=ROW, margin_bottom=15, align_items="center"))
        self.min_roe_input = toga.NumberInput(value=self._config['min_roe'] or self.DEFAULT_CONFIG['min_roe'], style=Pack(width=80))
        roe_box.add(self.min_roe_input)
        roe_box.add(toga.Label(" < ", style=Pack(margin_left=5, margin_right=5)))
        roe_box.add(toga.Label("ROE", style=Pack(margin_right=5)))
        roe_box.add(toga.Label(" < ", style=Pack(margin_right=5)))
        self.max_roe_input = toga.NumberInput(value=self._config['max_roe'] or self.DEFAULT_CONFIG['max_roe'], style=Pack(width=80))
        roe_box.add(self.max_roe_input)
        content_box.add(roe_label)
        content_box.add(roe_box)
        
        # 分红率范围
        bonus_label = toga.Label("分红率范围(%):", style=Pack(margin_bottom=5))
        bonus_box = toga.Box(style=Pack(direction=ROW, margin_bottom=15, align_items="center"))
        self.min_bonus_input = toga.NumberInput(value=self._config['min_bonus_rate'] or self.DEFAULT_CONFIG['min_bonus_rate'], style=Pack(width=80))
        bonus_box.add(self.min_bonus_input)
        bonus_box.add(toga.Label(" < ", style=Pack(margin_left=5, margin_right=5)))
        bonus_box.add(toga.Label("分红率", style=Pack(margin_right=5)))
        bonus_box.add(toga.Label(" < ", style=Pack(margin_right=5)))
        self.max_bonus_input = toga.NumberInput(value=self._config['max_bonus_rate'] or self.DEFAULT_CONFIG['max_bonus_rate'], style=Pack(width=80))
        bonus_box.add(self.max_bonus_input)
        content_box.add(bonus_label)
        content_box.add(bonus_box)
        
        # ROE稳定性范围
        roe_stability_label = toga.Label("ROE稳定性范围:", style=Pack(margin_bottom=5))
        roe_stability_box = toga.Box(style=Pack(direction=ROW, margin_bottom=15, align_items="center"))
        self.min_roe_stability_input = toga.NumberInput(value=self._config['min_roe_stability'] or self.DEFAULT_CONFIG['min_roe_stability'], style=Pack(width=80))
        roe_stability_box.add(self.min_roe_stability_input)
        roe_stability_box.add(toga.Label(" < ", style=Pack(margin_left=5, margin_right=5)))
        roe_stability_box.add(toga.Label("稳定性", style=Pack(margin_right=5)))
        roe_stability_box.add(toga.Label(" < ", style=Pack(margin_right=5)))
        self.max_roe_stability_input = toga.NumberInput(value=self._config['max_roe_stability'] or self.DEFAULT_CONFIG['max_roe_stability'], style=Pack(width=80))
        roe_stability_box.add(self.max_roe_stability_input)
        content_box.add(roe_stability_label)
        content_box.add(roe_stability_box)
        
        # ROE趋势范围
        roe_trend_label = toga.Label("ROE趋势范围:", style=Pack(margin_bottom=5))
        roe_trend_box = toga.Box(style=Pack(direction=ROW, margin_bottom=15, align_items="center"))
        self.min_roe_trend_input = toga.NumberInput(value=self._config['min_roe_trend'] or self.DEFAULT_CONFIG['min_roe_trend'], style=Pack(width=80))
        roe_trend_box.add(self.min_roe_trend_input)
        roe_trend_box.add(toga.Label(" < ", style=Pack(margin_left=5, margin_right=5)))
        roe_trend_box.add(toga.Label("趋势", style=Pack(margin_right=5)))
        roe_trend_box.add(toga.Label(" < ", style=Pack(margin_right=5)))
        self.max_roe_trend_input = toga.NumberInput(value=self._config['max_roe_trend'] or self.DEFAULT_CONFIG['max_roe_trend'], style=Pack(width=80))
        roe_trend_box.add(self.max_roe_trend_input)
        content_box.add(roe_trend_label)
        content_box.add(roe_trend_box)
        
        # 排序字段
        sort_by_label = toga.Label("排序字段:", style=Pack(margin_bottom=5))
        self.sort_by_selection = toga.Selection(
            items=['growth', 'pe', 'pb', 'roe', 'bonus_rate', 'assets_debt_ratio', 'roe_stability', 'roe_trend', 'growth / pb', 'growth / pe'],
            value=self._config['sort_by'] or self.DEFAULT_CONFIG['sort_by'],
            style=Pack(margin_bottom=15)
        )
        content_box.add(sort_by_label)
        content_box.add(self.sort_by_selection)
        
        # 排序顺序
        sort_order_label = toga.Label("排序顺序:", style=Pack(margin_bottom=5))
        self.sort_order_selection = toga.Selection(
            items=['desc', 'asc'],
            value=self._config['sort_order'] or self.DEFAULT_CONFIG['sort_order'],
            style=Pack(margin_bottom=20)
        )
        content_box.add(sort_order_label)
        content_box.add(self.sort_order_selection)
        
        # 创建滚动容器并添加内容
        scroll_container = toga.ScrollContainer(style=Pack(flex=1))
        scroll_container.content = content_box
        
        # 将滚动容器添加到主容器
        self.add(scroll_container)

    def _on_save(self, widget):
        self._config['page_size'] = int(self.page_size_input.value) if self.page_size_input.value is not None else None
        self._config['max_debt_ratio'] = float(self.max_debt_input.value) if self.max_debt_input.value is not None else None
        self._config['min_pe'] = float(self.min_pe_input.value) if self.min_pe_input.value is not None else None
        self._config['max_pe'] = float(self.max_pe_input.value) if self.max_pe_input.value is not None else None
        self._config['min_pb'] = float(self.min_pb_input.value) if self.min_pb_input.value is not None else None
        self._config['max_pb'] = float(self.max_pb_input.value) if self.max_pb_input.value is not None else None
        self._config['min_roe'] = float(self.min_roe_input.value) if self.min_roe_input.value is not None else None
        self._config['max_roe'] = float(self.max_roe_input.value) if self.max_roe_input.value is not None else None
        self._config['min_bonus_rate'] = float(self.min_bonus_input.value) if self.min_bonus_input.value is not None else None
        self._config['max_bonus_rate'] = float(self.max_bonus_input.value) if self.max_bonus_input.value is not None else None
        self._config['min_roe_stability'] = float(self.min_roe_stability_input.value) if self.min_roe_stability_input.value is not None else None
        self._config['max_roe_stability'] = float(self.max_roe_stability_input.value) if self.max_roe_stability_input.value is not None else None
        self._config['min_roe_trend'] = float(self.min_roe_trend_input.value) if self.min_roe_trend_input.value is not None else None
        self._config['max_roe_trend'] = float(self.max_roe_trend_input.value) if self.max_roe_trend_input.value is not None else None
        self._config['sort_by'] = self.sort_by_selection.value
        self._config['sort_order'] = self.sort_order_selection.value
        
        if self._on_config_change_handler:
            self._on_config_change_handler(self._config)
        
        if self._on_back_handler:
            self._on_back_handler()