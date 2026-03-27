"""
stock filter application
"""
import os
from threading import Thread

import toga
from toga.style.pack import Pack

from database.connection import DatabaseConnectionManager
from services.a_stock_service import AStockService
from services.a_financial_service import AFinancialService
from services.a_bonus_service import ABonusService
from view.paginated_list import PaginatedListBox


class StockApp(toga.App):
    def startup(self):
        # 设置数据库路径
        self.db_path = os.path.join(self.paths.data, "finance.db")
        if not os.path.exists(self.paths.data):
            os.makedirs(self.paths.data, exist_ok=True)
        
        # 设置默认数据库名称
        db_manager = DatabaseConnectionManager()
        db_manager.set_default_db_name(self.db_path)
        
        # 创建主窗口内容
        container = toga.OptionContainer(content=[
            ("A股列表", PaginatedListBox(self.db_path, self.on_stock_select)),
            ("系统配置", self._create_config_box())
        ])
        
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = container
        self._create_toolbar()
        self.main_window.show()
    
    def _create_config_box(self):
        """创建系统配置页面"""
        table = toga.Table(
            headings=["配置项", "值"],
            data=[
                ("缓存路径", self.paths.cache),
                ("数据路径", self.paths.data),
            ],
            style=Pack(flex=1)
        )
        return toga.Box(children=[table])
    
    def _create_toolbar(self):
        """创建工具栏"""
        # 刷新A股数据按钮
        cmd_refresh_a_stock = toga.Command(
            action=self._refresh_a_stock_async,
            text="刷新股票数据",
            tooltip="从API刷新A股基础数据",
            icon="resources/icons/brutus",
        )
        self.main_window.toolbar.add(cmd_refresh_a_stock)
        
        # 刷新财务数据按钮
        cmd_refresh_financial = toga.Command(
            action=self._refresh_financial_async,
            text="刷新财务数据",
            tooltip="刷新A股财务数据",
            icon="resources/icons/brutus",
        )
        self.main_window.toolbar.add(cmd_refresh_financial)
        
        # 刷新分红数据按钮
        cmd_refresh_bonus = toga.Command(
            action=self._refresh_bonus_async,
            text="刷新分红数据",
            tooltip="刷新A股分红数据",
            icon="resources/icons/brutus",
        )
        self.main_window.toolbar.add(cmd_refresh_bonus)
    
    def _refresh_a_stock_async(self, command, **kwargs):
        """异步刷新A股数据"""
        def refresh_data():
            try:
                with AStockService() as service:
                    updated_count = service.refresh_stocks()
                    print(f"A股数据刷新完成，共更新 {updated_count} 只股票")
            except Exception as e:
                print(f"刷新A股数据失败: {e}")
        
        t = Thread(target=refresh_data)
        t.start()
    
    def _refresh_financial_async(self, command, **kwargs):
        """异步刷新财务数据"""
        def refresh_data():
            try:
                with AFinancialService() as service:
                    updated_count = service.refresh_financial_data()
                    print(f"财务数据刷新完成，共更新 {updated_count} 只股票")
            except Exception as e:
                print(f"刷新财务数据失败: {e}")
        
        t = Thread(target=refresh_data)
        t.start()
    
    def _refresh_bonus_async(self, command, **kwargs):
        """异步刷新分红数据"""
        def refresh_data():
            try:
                with ABonusService() as service:
                    updated_count = service.refresh_all()
                    print(f"分红数据刷新完成，共更新 {updated_count} 只股票")
            except Exception as e:
                print(f"刷新分红数据失败: {e}")
        
        t = Thread(target=refresh_data)
        t.start()
    
    def on_stock_select(self, widget):
        """股票选择回调"""
        if widget.selection:
            print(f"Selected stock: {widget.selection}")


def main():
    return StockApp()
