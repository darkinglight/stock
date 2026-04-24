import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW


class HkStockConfigView(toga.Box):

    DEFAULT_CONFIG = {
        'page_size': 100,
        'sort_by': 'roe / pb',
        'sort_order': 'desc',
        'min_pe': 0,
        'max_pe': 100,
        'min_pb': 0,
        'max_pb': 10,
        'min_roe': 0,
        'max_roe': 100,
        'max_assets_debt_ratio': 100,
        'min_net_asset_per_share': 0,
        'min_basic_eps': 0
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
        content_box = toga.Box(style=Pack(direction=COLUMN, margin=10))
        
        page_size_label = toga.Label("每页显示数量:", style=Pack(margin_bottom=5))
        self.page_size_input = toga.NumberInput(value=self._config['page_size'] or self.DEFAULT_CONFIG['page_size'], style=Pack(margin_bottom=15))
        content_box.add(page_size_label)
        content_box.add(self.page_size_input)
        
        pe_label = toga.Label("市盈率范围:", style=Pack(margin_bottom=5))
        pe_box = toga.Box(style=Pack(direction=ROW, margin_bottom=15, align_items="center"))
        self.min_pe_input = toga.NumberInput(value=self._config['min_pe'] or self.DEFAULT_CONFIG['min_pe'], step=0.1, style=Pack(width=80))
        pe_box.add(self.min_pe_input)
        pe_box.add(toga.Label(" < ", style=Pack(margin_left=5, margin_right=5)))
        pe_box.add(toga.Label("PE", style=Pack(margin_right=5)))
        pe_box.add(toga.Label(" < ", style=Pack(margin_right=5)))
        self.max_pe_input = toga.NumberInput(value=self._config['max_pe'] or self.DEFAULT_CONFIG['max_pe'], step=0.1, style=Pack(width=80))
        pe_box.add(self.max_pe_input)
        content_box.add(pe_label)
        content_box.add(pe_box)
        
        pb_label = toga.Label("市净率范围:", style=Pack(margin_bottom=5))
        pb_box = toga.Box(style=Pack(direction=ROW, margin_bottom=15, align_items="center"))
        self.min_pb_input = toga.NumberInput(value=self._config['min_pb'] or self.DEFAULT_CONFIG['min_pb'], step=0.1, style=Pack(width=80))
        pb_box.add(self.min_pb_input)
        pb_box.add(toga.Label(" < ", style=Pack(margin_left=5, margin_right=5)))
        pb_box.add(toga.Label("PB", style=Pack(margin_right=5)))
        pb_box.add(toga.Label(" < ", style=Pack(margin_right=5)))
        self.max_pb_input = toga.NumberInput(value=self._config['max_pb'] or self.DEFAULT_CONFIG['max_pb'], step=0.1, style=Pack(width=80))
        pb_box.add(self.max_pb_input)
        content_box.add(pb_label)
        content_box.add(pb_box)
        
        roe_label = toga.Label("ROE范围(%):", style=Pack(margin_bottom=5))
        roe_box = toga.Box(style=Pack(direction=ROW, margin_bottom=15, align_items="center"))
        self.min_roe_input = toga.NumberInput(value=self._config['min_roe'] or self.DEFAULT_CONFIG['min_roe'], step=0.1, style=Pack(width=80))
        roe_box.add(self.min_roe_input)
        roe_box.add(toga.Label(" < ", style=Pack(margin_left=5, margin_right=5)))
        roe_box.add(toga.Label("ROE", style=Pack(margin_right=5)))
        roe_box.add(toga.Label(" < ", style=Pack(margin_right=5)))
        self.max_roe_input = toga.NumberInput(value=self._config['max_roe'] or self.DEFAULT_CONFIG['max_roe'], step=0.1, style=Pack(width=80))
        roe_box.add(self.max_roe_input)
        content_box.add(roe_label)
        content_box.add(roe_box)
        
        max_debt_label = toga.Label("最大资产负债率(%):", style=Pack(margin_bottom=5))
        self.max_debt_input = toga.NumberInput(value=self._config['max_assets_debt_ratio'] or self.DEFAULT_CONFIG['max_assets_debt_ratio'], step=0.1, style=Pack(margin_bottom=15))
        content_box.add(max_debt_label)
        content_box.add(self.max_debt_input)
        
        min_bps_label = toga.Label("最小每股净资产:", style=Pack(margin_bottom=5))
        self.min_bps_input = toga.NumberInput(value=self._config['min_net_asset_per_share'] or self.DEFAULT_CONFIG['min_net_asset_per_share'], step=0.01, style=Pack(margin_bottom=15))
        content_box.add(min_bps_label)
        content_box.add(self.min_bps_input)
        
        min_eps_label = toga.Label("最小每股收益:", style=Pack(margin_bottom=5))
        self.min_eps_input = toga.NumberInput(value=self._config['min_basic_eps'] or self.DEFAULT_CONFIG['min_basic_eps'], step=0.01, style=Pack(margin_bottom=15))
        content_box.add(min_eps_label)
        content_box.add(self.min_eps_input)
        
        sort_by_label = toga.Label("排序字段:", style=Pack(margin_bottom=5))
        self.sort_by_selection = toga.Selection(
            items=['roe / pb', 'roe / pe', 'price', 'pe', 'pb', 'roe', 'assets_debt_ratio', 'net_asset_per_share', 'basic_eps'],
            value=self._config['sort_by'] or self.DEFAULT_CONFIG['sort_by'],
            style=Pack(margin_bottom=15)
        )
        content_box.add(sort_by_label)
        content_box.add(self.sort_by_selection)
        
        sort_order_label = toga.Label("排序顺序:", style=Pack(margin_bottom=5))
        self.sort_order_selection = toga.Selection(
            items=['desc', 'asc'],
            value=self._config['sort_order'] or self.DEFAULT_CONFIG['sort_order'],
            style=Pack(margin_bottom=20)
        )
        content_box.add(sort_order_label)
        content_box.add(self.sort_order_selection)
        
        save_button = toga.Button(
            "保存",
            on_press=self._on_save,
            style=Pack(margin=10, padding=10, width=200, align_items="center")
        )
        
        scroll_container = toga.ScrollContainer(style=Pack(flex=1))
        scroll_container.content = content_box
        
        self.add(scroll_container)
        self.add(save_button)

    def _on_save(self, widget):
        self._config['page_size'] = int(self.page_size_input.value) if self.page_size_input.value is not None else None
        self._config['min_pe'] = float(self.min_pe_input.value) if self.min_pe_input.value is not None else None
        self._config['max_pe'] = float(self.max_pe_input.value) if self.max_pe_input.value is not None else None
        self._config['min_pb'] = float(self.min_pb_input.value) if self.min_pb_input.value is not None else None
        self._config['max_pb'] = float(self.max_pb_input.value) if self.max_pb_input.value is not None else None
        self._config['min_roe'] = float(self.min_roe_input.value) if self.min_roe_input.value is not None else None
        self._config['max_roe'] = float(self.max_roe_input.value) if self.max_roe_input.value is not None else None
        self._config['max_assets_debt_ratio'] = float(self.max_debt_input.value) if self.max_debt_input.value is not None else None
        self._config['min_net_asset_per_share'] = float(self.min_bps_input.value) if self.min_bps_input.value is not None else None
        self._config['min_basic_eps'] = float(self.min_eps_input.value) if self.min_eps_input.value is not None else None
        self._config['sort_by'] = self.sort_by_selection.value
        self._config['sort_order'] = self.sort_order_selection.value
        
        if self._on_config_change_handler:
            self._on_config_change_handler(self._config)
        
        if self._on_back_handler:
            self._on_back_handler()