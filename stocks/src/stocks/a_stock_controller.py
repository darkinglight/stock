import toga
from services.a_stock_service import AStockService
from services.a_bonus_service import ABonusService
from services.a_financial_service import AFinancialService
from services.config_service import ConfigService
from view.a_stock_list import StockListView
from view.a_stock_config import StockConfigView
from view.a_stock_detail import StockDetailView
from view.a_stock_task import StockTaskView


class AStockController:
    def __init__(self, main_window=None):
        self.main_window = main_window
        self.stock_list_view = None
        self.stock_config_view = None
        self.stock_detail_view = None
        self.stock_task_view = None
        self.detail_window = None
        self.service = AStockService()
        self.bonus_service = ABonusService()
        self.financial_service = AFinancialService()
        self.config_service = ConfigService()
        self._config = self.config_service.load_stock_list_config()
        self.is_updating = False
        self.update_thread = None

    def initialize_stock_list(self):
        stocks_data = self.get_stocks_data(self._config)

        self.stock_list_view = StockListView(
            stocks=stocks_data,
            on_select=self.on_stock_select
        )
        self.stock_config_view = StockConfigView(
            on_config_change=self.on_config_change,
            on_back=self.on_back,
            default_config=self._config
        )
        self.stock_task_view = StockTaskView(
            on_start_update=self.on_start_update,
            on_pause_update=self.on_pause_update
        )
        return self.stock_list_view
    
    def get_stocks_data(self, config):
        stocks_data = self.service.get_stocks_paginated(
            page=1,
            page_size=config['page_size'],
            sort_by=config['sort_by'],
            sort_order=config['sort_order'],
            max_debt_ratio=config.get('max_debt_ratio'),
            min_pe=config.get('min_pe'),
            max_pe=config.get('max_pe'),
            min_pb=config.get('min_pb'),
            max_pb=config.get('max_pb'),
            min_roe=config.get('min_roe'),
            max_roe=config.get('max_roe'),
            min_bonus_rate=config.get('min_bonus_rate'),
            max_bonus_rate=config.get('max_bonus_rate'),
            min_roe_stability=config.get('min_roe_stability'),
            max_roe_stability=config.get('max_roe_stability'),
            min_roe_trend=config.get('min_roe_trend'),
            max_roe_trend=config.get('max_roe_trend')
        )
        return stocks_data
    
    def show_config_dialog(self, widget=None):
        if self.stock_config_view and self.main_window:
            # 清空工具栏并添加配置页面的命令
            self.main_window.toolbar.clear()
            for command in self.get_config_toolbar_commands():
                self.main_window.toolbar.add(command)
            # 切换到配置页面
            self.main_window.content = self.stock_config_view
            self.main_window.title = "列表配置"

    def on_back(self, widget=None):
        if self.stock_list_view and self.main_window:
            # 清空工具栏并添加股票列表页面的命令
            self.main_window.toolbar.clear()
            for command in self.get_toolbar_commands():
                self.main_window.toolbar.add(command)
            # 重新加载数据以确保显示最新配置
            stocks_data = self.get_stocks_data(self._config)
            self.stock_list_view.update_data(stocks_data)
            self.main_window.content = self.stock_list_view
            self.main_window.title = "股票列表"
    
    def get_toolbar_commands(self):
        cmd_config = toga.Command(
            action=self.show_config_dialog,
            text="配置",
            tooltip="列表配置",
            icon="resources/config.png"
        )
        cmd_task = toga.Command(
            action=self.show_task_dialog,
            text="任务",
            tooltip="任务管理",
            icon="resources/work.png"
        )
        return [cmd_config, cmd_task]
    
    def get_config_toolbar_commands(self):
        cmd_save = toga.Command(
            action=self._on_config_save,
            text="保存",
            tooltip="保存配置",
            icon="resources/save.png"
        )
        cmd_back = toga.Command(
            action=self.on_back,
            text="返回",
            tooltip="返回股票列表",
            icon="resources/back.png"
        )
        return [cmd_back, cmd_save]
    
    def _on_config_save(self, widget):
        # 触发保存操作
        if self.stock_config_view:
            # 模拟点击保存按钮
            self.stock_config_view._on_save(widget)
    
    def on_config_change(self, config):
        self._config = config
        self.config_service.save_stock_list_config(config)
        stocks_data = self.get_stocks_data(config)
        if self.stock_list_view:
            self.stock_list_view.update_data(stocks_data)
    
    def show_task_dialog(self, widget=None):
        if self.stock_task_view and self.main_window:
            # 清空工具栏并添加任务页面的命令
            self.main_window.toolbar.clear()
            for command in self.get_task_toolbar_commands():
                self.main_window.toolbar.add(command)
            # 切换到任务页面
            self.main_window.content = self.stock_task_view
            self.main_window.title = "任务管理"

    def get_task_toolbar_commands(self):
        cmd_back = toga.Command(
            action=self.on_back,
            text="返回",
            tooltip="返回股票列表",
            icon="resources/back.png"
        )
        return [cmd_back]

    def on_start_update(self, widget=None):
        """开始更新任务"""
        if self.is_updating:
            return
        
        self.is_updating = True
        self.stock_task_view.set_button_states(False, True)
        self.stock_task_view.update_overall_status("更新中")
        
        # 启动更新线程
        import threading
        self.update_thread = threading.Thread(target=self._perform_update)
        self.update_thread.daemon = True
        self.update_thread.start()

    def on_pause_update(self, widget=None):
        """暂停更新任务"""
        self.is_updating = False
        if self.update_thread:
            self.update_thread.join(timeout=1)
        self.stock_task_view.set_button_states(True, False)
        self.stock_task_view.update_overall_status("已暂停")

    def _perform_update(self):
        """执行更新任务"""
        try:
            # 更新Stock
            self.stock_task_view.update_task_status("Stock刷新", "进行中", 0)
            self.stock_task_view.update_progress(0)
            # 模拟Stock更新过程
            import time
            for i in range(1, 34):
                if not self.is_updating:
                    break
                time.sleep(0.1)
                progress = i
                self.stock_task_view.update_task_status("Stock刷新", "进行中", progress)
                self.stock_task_view.update_progress(progress)
            
            if not self.is_updating:
                return
            
            # 更新Financial
            self.stock_task_view.update_task_status("Stock刷新", "完成", 100)
            self.stock_task_view.update_task_status("Financial更新", "进行中", 0)
            for i in range(1, 34):
                if not self.is_updating:
                    break
                time.sleep(0.1)
                progress = 33 + i
                self.stock_task_view.update_task_status("Financial更新", "进行中", progress - 33)
                self.stock_task_view.update_progress(progress)
            
            if not self.is_updating:
                return
            
            # 更新Bonus
            self.stock_task_view.update_task_status("Financial更新", "完成", 100)
            self.stock_task_view.update_task_status("Bonus更新", "进行中", 0)
            for i in range(1, 34):
                if not self.is_updating:
                    break
                time.sleep(0.1)
                progress = 66 + i
                self.stock_task_view.update_task_status("Bonus更新", "进行中", progress - 66)
                self.stock_task_view.update_progress(progress)
            
            if self.is_updating:
                # 更新完成
                self.stock_task_view.update_task_status("Bonus更新", "完成", 100)
                self.stock_task_view.update_progress(100)
                self.stock_task_view.update_overall_status("更新完成")
                # 更新最近更新日期
                from datetime import datetime
                current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.stock_task_view.update_last_update_date(current_date)
        finally:
            self.is_updating = False
            self.stock_task_view.set_button_states(True, False)

    def on_stock_select(self, row):
        """
        处理股票选择事件
        :param row: 选中的行数据
        """
        if not row:
            return
        
        # 获取选中股票的代码
        stock_code = row[1]  # 代码在第二列
        
        # 获取股票详情、财报数据和分红数据
        stock = self.service.get_stock_by_code(stock_code)
        financial_reports = self.financial_service.get_financial_reports_by_code(stock_code)
        bonus_details = self.bonus_service.get_bonus_details_by_code(stock_code)
        
        if not stock:
            return
        
        # 创建股票详情视图
        if not self.stock_detail_view:
            self.stock_detail_view = StockDetailView()
        
        # 更新详情视图数据
        self.stock_detail_view.update_data(stock, financial_reports, bonus_details)
        
        # 使用复用的窗口显示详情页面
        if not self.detail_window:
            self.detail_window = toga.Window(
                title=f"{stock.name} 详情",
                size=(800, 600),
                resizable=True,
                content=self.stock_detail_view,
                on_resize=None,
                on_gain_focus=None,
                on_lose_focus=None,
                on_show=None,
                on_hide=None
            )
        else:
            self.detail_window.title = f"{stock.name} 详情"
            self.detail_window.content = self.stock_detail_view
        
        self.detail_window.show()

