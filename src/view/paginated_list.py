from pathlib import Path

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, LEFT, RIGHT, CENTER

from services.a_stock_service import AStockService


class PaginatedListBox(toga.Box):
    cache = dict()

    def __init__(self, data_path: Path, on_active):
        self.db_file = data_path
        self.on_active = on_active
        self.current_page = 1
        self.page_size = 10
        self.sort_by = 'growth'
        self.sort_order = 'desc'
        self.service = AStockService()
        
        # 创建主容器
        super().__init__(style=Pack(direction=COLUMN, flex=1))
        
        # 添加控件
        self.add(self._create_filter_box())
        self.table = self._create_table()
        self.add(self.table)
        self.add(self._create_pagination_box())
        
        # 加载初始数据
        self.load_data()

    def _create_filter_box(self):
        """创建筛选和排序控件"""
        filter_box = toga.Box(style=Pack(direction=ROW, padding=5))
        
        # 排序字段选择
        sort_by_label = toga.Label('排序字段:', style=Pack(width=100))
        self.sort_by_input = toga.Selection(
            items=['growth', 'pe'],
            style=Pack(width=100)
        )
        self.sort_by_input.value = self.sort_by
        self.sort_by_input.on_select = self.on_sort_change
        
        # 排序顺序选择
        sort_order_label = toga.Label('排序顺序:', style=Pack(width=100))
        self.sort_order_input = toga.Selection(
            items=['asc', 'desc'],
            style=Pack(width=100)
        )
        self.sort_order_input.value = self.sort_order
        self.sort_order_input.on_select = self.on_sort_change
        
        # 每页数量选择
        page_size_label = toga.Label('每页数量:', style=Pack(width=100))
        self.page_size_input = toga.Selection(
            items=['10', '20', '50'],
            style=Pack(width=100)
        )
        self.page_size_input.value = str(self.page_size)
        self.page_size_input.on_select = self.on_page_size_change
        
        # 添加到筛选框
        filter_box.add(sort_by_label)
        filter_box.add(self.sort_by_input)
        filter_box.add(sort_order_label)
        filter_box.add(self.sort_order_input)
        filter_box.add(page_size_label)
        filter_box.add(self.page_size_input)
        
        return filter_box

    def _create_table(self):
        """创建股票列表表格"""
        headings = ["代码", "名称", "市场", "价格", "市盈率", "市净率", "分红率", "每股净资产", "每股收益", "资产负债率", "净资产收益率", "内在增长率"]
        return toga.Table(
            headings=headings,
            data=[],
            on_select=self.on_active,
            style=Pack(flex=1)
        )

    def _create_pagination_box(self):
        """创建分页控件"""
        pagination_box = toga.Box(style=Pack(direction=ROW, padding=5, alignment=CENTER))
        
        # 上一页按钮
        self.prev_button = toga.Button(
            '上一页',
            on_press=self.on_prev_page,
            style=Pack(width=100)
        )
        
        # 页码输入
        self.page_input = toga.TextInput(
            value=str(self.current_page),
            style=Pack(width=50)
        )
        self.page_input.on_change = self.on_page_change
        
        # 总页数显示
        self.total_pages_label = toga.Label(
            f'/ {self.current_page}',
            style=Pack(width=50, text_align=CENTER)
        )
        
        # 下一页按钮
        self.next_button = toga.Button(
            '下一页',
            on_press=self.on_next_page,
            style=Pack(width=100)
        )
        
        # 总记录数显示
        self.total_count_label = toga.Label(
            '总记录数: 0',
            style=Pack(width=150, text_align=RIGHT)
        )
        
        # 添加到分页框
        pagination_box.add(self.prev_button)
        pagination_box.add(self.page_input)
        pagination_box.add(self.total_pages_label)
        pagination_box.add(self.next_button)
        pagination_box.add(self.total_count_label)
        
        return pagination_box

    def load_data(self):
        """加载分页数据"""
        # 调用服务获取数据
        result = self.service.get_stocks_paginated(
            page=self.current_page,
            page_size=self.page_size,
            sort_by=self.sort_by,
            sort_order=self.sort_order
        )
        
        # 更新表格数据
        stocks = result['stocks']
        table_data = []
        for stock in stocks:
            table_data.append((
                stock.code,
                stock.name,
                stock.market,
                stock.price if stock.price else 0,
                stock.pe if stock.pe else 0,
                stock.pb if stock.pb else 0,
                stock.bonus_rate if stock.bonus_rate else 0,
                stock.net_asset_per_share if stock.net_asset_per_share else 0,
                stock.basic_eps if stock.basic_eps else 0,
                stock.assets_debt_ratio if stock.assets_debt_ratio else 0,
                stock.roe if stock.roe else 0,
                stock.growth if stock.growth else 0
            ))
        
        # 清空并重新添加数据
        self.table.data = table_data
        
        # 更新分页信息
        self.total_count = result['total_count']
        self.total_pages = result['total_pages']
        self.total_pages_label.text = f'/ {self.total_pages}'
        self.total_count_label.text = f'总记录数: {self.total_count}'
        
        # 更新按钮状态
        self.prev_button.enabled = self.current_page > 1
        self.next_button.enabled = self.current_page < self.total_pages

    def on_sort_change(self, widget):
        """排序选项改变时的处理"""
        self.sort_by = self.sort_by_input.value
        self.sort_order = self.sort_order_input.value
        self.current_page = 1
        self.page_input.value = str(self.current_page)
        self.load_data()

    def on_page_size_change(self, widget):
        """每页数量改变时的处理"""
        self.page_size = int(self.page_size_input.value)
        self.current_page = 1
        self.page_input.value = str(self.current_page)
        self.load_data()

    def on_page_change(self, widget):
        """页码输入改变时的处理"""
        try:
            new_page = int(self.page_input.value)
            if new_page >= 1 and new_page <= self.total_pages:
                self.current_page = new_page
                self.load_data()
        except ValueError:
            # 输入不是数字，恢复当前页码
            self.page_input.value = str(self.current_page)

    def on_prev_page(self, widget):
        """上一页按钮点击时的处理"""
        if self.current_page > 1:
            self.current_page -= 1
            self.page_input.value = str(self.current_page)
            self.load_data()

    def on_next_page(self, widget):
        """下一页按钮点击时的处理"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.page_input.value = str(self.current_page)
            self.load_data()
