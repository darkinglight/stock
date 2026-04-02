from typing import Optional, Dict, Any

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER


class StockDetailView(toga.Box):

    def __init__(self):
        super().__init__(style=Pack(flex=1, direction=COLUMN, padding=10))
        
        # 创建标题
        self.title = toga.Label(
            "股票详情",
            style=Pack(font_size=18, font_weight='bold', margin_bottom=10)
        )
        self.add(self.title)
        
        # 创建基本信息区域
        self.basic_info = toga.Box(style=Pack(direction=ROW, margin_bottom=10))
        self.add(self.basic_info)
        
        # 创建财报数据区域
        self.financial_section = toga.Box(style=Pack(direction=COLUMN, margin_bottom=10))
        self.add(self.financial_section)
        
        # 创建分红数据区域
        self.bonus_section = toga.Box(style=Pack(direction=COLUMN))
        self.add(self.bonus_section)
    
    def update_data(self, stock_data: Dict[str, Any], financial_data: Dict[str, Any], bonus_data: Dict[str, Any]):
        # 清空现有内容
        self.basic_info.clear()
        self.financial_section.clear()
        self.bonus_section.clear()
        
        # 更新标题
        self.title.text = f"{stock_data.get('name', '')} ({stock_data.get('code', '')})"
        
        # 更新基本信息
        basic_info_box = toga.Box(style=Pack(direction=COLUMN, flex=1))
        basic_info_box.add(toga.Label(f"价格: {stock_data.get('price', '-')}", style=Pack(margin=2)))
        basic_info_box.add(toga.Label(f"PE: {stock_data.get('pe', '-')}", style=Pack(margin=2)))
        basic_info_box.add(toga.Label(f"PB: {stock_data.get('pb', '-')}", style=Pack(margin=2)))
        basic_info_box.add(toga.Label(f"分红率: {stock_data.get('bonus_rate', '-')}%", style=Pack(margin=2)))
        basic_info_box.add(toga.Label(f"资产负债率: {stock_data.get('assets_debt_ratio', '-')}%", style=Pack(margin=2)))
        basic_info_box.add(toga.Label(f"ROE: {stock_data.get('roe', '-')}%", style=Pack(margin=2)))
        basic_info_box.add(toga.Label(f"内在增长率: {stock_data.get('growth', '-')}%", style=Pack(margin=2)))
        self.basic_info.add(basic_info_box)
        
        # 更新财报数据
        financial_title = toga.Label("财报数据", style=Pack(font_size=14, font_weight='bold', margin_bottom=5))
        self.financial_section.add(financial_title)
        
        if financial_data:
            financial_table = toga.Table(
                headings=["指标", "值"],
                data=[
                    ("每股净资产", financial_data.get('net_asset_per_share', '-')),
                    ("每股收益", financial_data.get('basic_eps', '-')),
                    ("营业收入", financial_data.get('revenue', '-')),
                    ("净利润", financial_data.get('net_profit', '-')),
                    ("毛利率", financial_data.get('gross_profit_rate', '-')),
                    ("净利率", financial_data.get('net_profit_rate', '-')),
                ],
                style=Pack(flex=1)
            )
            self.financial_section.add(financial_table)
        else:
            self.financial_section.add(toga.Label("暂无财报数据", style=Pack(margin=5)))
        
        # 如果有财报历史数据，显示历史财报列表
        if 'reports' in financial_data and financial_data['reports']:
            history_title = toga.Label("历史财报数据", style=Pack(font_size=14, font_weight='bold', margin_top=10, margin_bottom=5))
            self.financial_section.add(history_title)
            
            history_table = toga.Table(
                headings=["报告期", "ROE", "每股净资产", "每股收益", "资产负债率"],
                data=[
                    (report.get('report_period', '-'), 
                     report.get('roe', '-'), 
                     report.get('net_asset_per_share', '-'), 
                     report.get('basic_eps', '-'), 
                     report.get('assets_debt_ratio', '-'))
                    for report in financial_data['reports']
                ],
                style=Pack(flex=1)
            )
            self.financial_section.add(history_table)
        
        # 更新分红数据
        bonus_title = toga.Label("分红数据", style=Pack(font_size=14, font_weight='bold', margin_bottom=5))
        self.bonus_section.add(bonus_title)
        
        if bonus_data:
            bonus_table = toga.Table(
                headings=["年份", "分红金额", "分红率"],
                data=[
                    (item.get('year', '-'), item.get('amount', '-'), item.get('rate', '-'))
                    for item in bonus_data.get('history', [])
                ],
                style=Pack(flex=1)
            )
            self.bonus_section.add(bonus_table)
        else:
            self.bonus_section.add(toga.Label("暂无分红数据", style=Pack(margin=5)))
