import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW


class StockDetailView(toga.Box):

    def __init__(self):
        super().__init__(style=Pack(flex=1, direction=COLUMN, margin=10))
        
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
    
    def update_data(self, stock, financial_reports, bonus_details):
        # 清空现有内容
        self.basic_info.clear()
        self.financial_section.clear()
        self.bonus_section.clear()
        
        # 更新标题
        self.title.text = f"{stock.name} ({stock.code})"
        
        # 更新基本信息
        basic_info_box = toga.Box(style=Pack(direction=COLUMN, flex=1))
        basic_info_box.add(toga.Label(f"价格: {stock.price if stock.price else '-'}", style=Pack(margin=2)))
        basic_info_box.add(toga.Label(f"PE: {stock.pe if stock.pe else '-'}", style=Pack(margin=2)))
        basic_info_box.add(toga.Label(f"PB: {stock.pb if stock.pb else '-'}", style=Pack(margin=2)))
        basic_info_box.add(toga.Label(f"分红率: {stock.bonus_rate if stock.bonus_rate else '-'}%", style=Pack(margin=2)))
        basic_info_box.add(toga.Label(f"资产负债率: {stock.assets_debt_ratio if stock.assets_debt_ratio else '-'}%", style=Pack(margin=2)))
        basic_info_box.add(toga.Label(f"ROE: {stock.roe if stock.roe else '-'}%", style=Pack(margin=2)))
        basic_info_box.add(toga.Label(f"内在增长率: {stock.growth if stock.growth else '-'}%", style=Pack(margin=2)))
        self.basic_info.add(basic_info_box)
        
        # 更新财报数据
        financial_title = toga.Label("财报数据", style=Pack(font_size=14, font_weight='bold', margin_bottom=5))
        self.financial_section.add(financial_title)
        
        if financial_reports:
            latest_report = financial_reports[0]
            financial_table = toga.Table(
                headings=["指标", "值"],
                data=[
                    ("每股净资产", latest_report.net_asset_per_share if latest_report.net_asset_per_share else '-'),
                    ("每股收益", latest_report.basic_eps if latest_report.basic_eps else '-'),
                    ("营业收入", "-"),  # 暂时返回-，后续可以从API获取
                    ("净利润", "-"),  # 暂时返回-，后续可以从API获取
                    ("毛利率", "-"),  # 暂时返回-，后续可以从API获取
                    ("净利率", "-"),  # 暂时返回-，后续可以从API获取
                ],
                style=Pack(flex=1)
            )
            self.financial_section.add(financial_table)
        else:
            self.financial_section.add(toga.Label("暂无财报数据", style=Pack(margin=5)))
        
        # 如果有财报历史数据，显示历史财报列表
        if financial_reports:
            history_title = toga.Label("历史财报数据", style=Pack(font_size=14, font_weight='bold', margin_top=10, margin_bottom=5))
            self.financial_section.add(history_title)
            
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
                style=Pack(flex=1)
            )
            self.financial_section.add(history_table)
        
        # 更新分红数据
        bonus_title = toga.Label("分红数据", style=Pack(font_size=14, font_weight='bold', margin_bottom=5))
        self.bonus_section.add(bonus_title)
        
        if bonus_details:
            bonus_table = toga.Table(
                headings=["年份", "分红金额", "分红率"],
                data=[
                    (bonus.year if bonus.year else '-', 
                     bonus.bonus_amount if bonus.bonus_amount else '-', 
                     bonus.dividend_payout_rate if bonus.dividend_payout_rate else '-')
                    for bonus in bonus_details
                ],
                style=Pack(flex=1)
            )
            self.bonus_section.add(bonus_table)
        else:
            self.bonus_section.add(toga.Label("暂无分红数据", style=Pack(margin=5)))
