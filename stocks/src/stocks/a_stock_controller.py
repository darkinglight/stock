import asyncio
import threading

import toga
from toga.style import Pack
from toga.style.pack import COLUMN
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
        self.service = AStockService()
        self.bonus_service = ABonusService()
        self.financial_service = AFinancialService()
        self.config_service = ConfigService()
        self._config = self.config_service.load_stock_list_config()
        self.task_threads = {}
        self.task_running = {}
        self._loop = None

    def initialize_stock_list(self):
        self._loop = asyncio.get_event_loop()
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
            self.main_window.content = self.stock_config_view
            self.main_window.title = "列表配置"

    def on_back(self, widget=None):
        if self.stock_list_view and self.main_window:
            stocks_data = self.get_stocks_data(self._config)
            self.stock_list_view.update_data(stocks_data)
            main_box = toga.Box(style=Pack(flex=1, direction=COLUMN))
            main_box.add(self.stock_list_view)
            self.main_window.content = main_box
            self.main_window.title = "股票列表"
    
    def refresh_stock_list(self, widget=None):
        if self.stock_list_view and self.main_window:
            stocks_data = self.get_stocks_data(self._config)
            self.stock_list_view.update_data(stocks_data)
    
    def get_toolbar_commands(self):
        cmd_stock_list = toga.Command(
            action=self.on_back,
            text="A股列表",
            tooltip="返回A股列表",
            icon="resources/back.png"
        )
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
        return [cmd_stock_list, cmd_config, cmd_task]
    
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
            self.main_window.content = self.stock_task_view
            self.main_window.title = "任务管理"

    def on_start_update(self, task_name: str):
        """开始更新指定任务"""
        if self.task_running.get(task_name, False):
            return

        self.task_running[task_name] = True
        self.stock_task_view.set_task_running(task_name, True)
        self.stock_task_view.update_task_status(task_name, "进行中", 0)

        thread = threading.Thread(target=self._perform_task_update, args=(task_name,))
        thread.daemon = True
        thread.start()
        self.task_threads[task_name] = thread

    def on_pause_update(self, task_name: str):
        """暂停更新指定任务"""
        self.task_running[task_name] = False
        if task_name in self.task_threads:
            self.task_threads[task_name].join(timeout=1)
        self.stock_task_view.set_task_running(task_name, False)
        self.stock_task_view.update_task_status(task_name, "已暂停", 0)

    def _update_ui_safe(self, task_name: str, status: str, progress: float):
        """线程安全地更新UI"""
        if self.stock_task_view:
            self.stock_task_view.update_task_status(task_name, status, progress)

    def _set_running_safe(self, task_name: str, running: bool):
        """线程安全地设置运行状态"""
        if self.stock_task_view:
            self.stock_task_view.set_task_running(task_name, running)

    def _create_progress_callback(self, task_name: str):
        """创建进度回调函数，支持阶段名称"""
        def callback(current: int, total: int, phase: str = ""):
            if not self.task_running.get(task_name, False):
                return
            progress = round(current / total * 100, 2) if total > 0 else 0
            status = f"{phase}" if phase else "进行中"
            if self._loop:
                self._loop.call_soon_threadsafe(self._update_ui_safe, task_name, status, progress)
        return callback

    def _perform_task_update(self, task_name: str):
        """执行单个任务更新"""
        try:
            progress_callback = self._create_progress_callback(task_name)
            # 创建停止检查回调
            should_stop = lambda: not self.task_running.get(task_name, False)
            
            if task_name == "Stock刷新":
                self.service.refresh_stocks(progress_callback)
            elif task_name == "Financial更新":
                self.financial_service.refresh_financial_data(progress_callback, should_stop)
            elif task_name == "Bonus更新":
                self.bonus_service.refresh_all(progress_callback, should_stop)
            
            if self.task_running.get(task_name, False):
                if self._loop:
                    self._loop.call_soon_threadsafe(self._update_ui_safe, task_name, "完成", 100)
        finally:
            self.task_running[task_name] = False
            if self._loop:
                self._loop.call_soon_threadsafe(self._set_running_safe, task_name, False)

    def on_stock_select(self, row):
        """
        处理股票选择事件
        :param row: 选中的行数据
        """
        if not row:
            return
        
        stock_code = row[1]
        stock_name = row[2]
        
        financial_reports = self.financial_service.get_financial_reports_by_code(stock_code)
        bonus_details = self.bonus_service.get_bonus_details_by_code(stock_code)
        
        if not self.stock_detail_view:
            self.stock_detail_view = StockDetailView()
        
        self.stock_detail_view.update_data(stock_code, stock_name, financial_reports, bonus_details)
        
        if self.main_window:
            self.main_window.toolbar.clear()
            for command in self.get_toolbar_commands():
                self.main_window.toolbar.add(command)
            self.main_window.content = self.stock_detail_view
            self.main_window.title = f"{stock_name} 详情"
    
