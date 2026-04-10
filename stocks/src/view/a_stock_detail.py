import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW


class StockDetailView(toga.Box):

    def __init__(self):
        super().__init__(style=Pack(flex=1, direction=COLUMN))
        
        self.content_box = toga.Box(style=Pack(direction=COLUMN, margin=10))
        
        self.title = toga.Label(
            "股票详情",
            style=Pack(font_size=18, font_weight='bold', margin_bottom=10)
        )
        self.content_box.add(self.title)
        
        self.scroll_container = toga.ScrollContainer(
            content=self.content_box,
            style=Pack(flex=1)
        )
        self.add(self.scroll_container)
    
    def update_data(self, stock_code, stock_name, financial_reports, bonus_details):
        self.content_box.clear()
        self.content_box.add(self.title)
        
        self.title.text = f"{stock_name} ({stock_code})"
        
        financial_title = toga.Label("历史财报数据", style=Pack(font_size=14, font_weight='bold', margin_bottom=5, margin_top=10))
        self.content_box.add(financial_title)
        
        if financial_reports:
            history_table = toga.Table(
                headings=["报告期", "ROE", "每股净资产", "每股收益", "资产负债率"],
                data=[
                    (report.report_period if report.report_period else '-', 
                     report.roe if report.roe else '-', 
                     report.net_asset_per_share if report.net_asset_per_share else '-', 
                     report.basic_eps if report.basic_eps else '-', 
                     report.assets_debt_ratio if report.assets_debt_ratio else '-')
                    for report in financial_reports
                ],
                style=Pack()
            )
            self.content_box.add(history_table)
        else:
            self.content_box.add(toga.Label("暂无财报数据", style=Pack(margin=5)))
        
        bonus_title = toga.Label("历史分红数据", style=Pack(font_size=14, font_weight='bold', margin_bottom=5, margin_top=10))
        self.content_box.add(bonus_title)
        
        if bonus_details:
            bonus_table = toga.Table(
                headings=["年份", "分红金额", "分红率"],
                data=[
                    (bonus.report_period if bonus.report_period else '-', 
                     bonus.bonus_amount if bonus.bonus_amount else '-', 
                     bonus.dividend_payout_rate if bonus.dividend_payout_rate else '-')
                    for bonus in bonus_details
                ],
                style=Pack()
            )
            self.content_box.add(bonus_table)
        else:
            self.content_box.add(toga.Label("暂无分红数据", style=Pack(margin=5)))
        
        self.refresh()
