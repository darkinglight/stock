from typing import Optional, Callable

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER, RIGHT


class StockTaskView(toga.Box):

    def __init__(self, on_start_update: Optional[Callable] = None, on_pause_update: Optional[Callable] = None):
        self._on_start_update_handler = on_start_update
        self._on_pause_update_handler = on_pause_update
        
        super().__init__(style=Pack(flex=1, direction=COLUMN, padding=10))

        # 创建标题
        self.title = toga.Label(
            "任务管理", 
            style=Pack(font_size=18, font_weight='bold', padding_bottom=10)
        )
        self.add(self.title)

        # 创建最近更新日期区域
        self.update_date_box = toga.Box(style=Pack(direction=ROW, padding=5))
        self.update_date_label = toga.Label("最近更新日期:", style=Pack(width=120))
        self.update_date_value = toga.Label("未更新", style=Pack(flex=1))
        self.update_date_box.add(self.update_date_label)
        self.update_date_box.add(self.update_date_value)
        self.add(self.update_date_box)

        # 创建任务状态区域
        self.status_box = toga.Box(style=Pack(direction=ROW, padding=5))
        self.status_label = toga.Label("任务状态:", style=Pack(width=120))
        self.status_value = toga.Label("就绪", style=Pack(flex=1))
        self.status_box.add(self.status_label)
        self.status_box.add(self.status_value)
        self.add(self.status_box)

        # 创建进度条区域
        self.progress_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
        self.progress_label = toga.Label("更新进度:", style=Pack(padding_bottom=5))
        self.progress_bar = toga.ProgressBar(max=100, value=0, style=Pack(height=20, margin_bottom=5))
        self.progress_text = toga.Label("0%", style=Pack(text_align=RIGHT))
        self.progress_box.add(self.progress_label)
        self.progress_box.add(self.progress_bar)
        self.progress_box.add(self.progress_text)
        self.add(self.progress_box)

        # 创建按钮区域
        self.button_box = toga.Box(style=Pack(direction=ROW, padding=5, alignment=CENTER))
        self.start_button = toga.Button(
            "开始更新", 
            on_press=self._on_start_update, 
            style=Pack(width=100, margin_right=10)
        )
        self.pause_button = toga.Button(
            "暂停更新", 
            on_press=self._on_pause_update, 
            style=Pack(width=100),
            enabled=False
        )
        self.button_box.add(self.start_button)
        self.button_box.add(self.pause_button)
        self.add(self.button_box)

        # 创建任务列表区域
        self.task_list_box = toga.Box(style=Pack(direction=COLUMN, padding=5, flex=1))
        self.task_list_label = toga.Label("任务列表:", style=Pack(padding_bottom=5))
        self.task_list = toga.Table(
            headings=["任务名称", "状态", "进度"],
            accessors=["name", "status", "progress"],
            data=[
                ("Stock刷新", "就绪", "0%"),
                ("Financial更新", "就绪", "0%"),
                ("Bonus更新", "就绪", "0%"),
            ],
            style=Pack(flex=1)
        )
        self.task_list_box.add(self.task_list_label)
        self.task_list_box.add(self.task_list)
        self.add(self.task_list_box)

    def _on_start_update(self, widget):
        if self._on_start_update_handler:
            self._on_start_update_handler()

    def _on_pause_update(self, widget):
        if self._on_pause_update_handler:
            self._on_pause_update_handler()

    def update_task_status(self, task_name, status, progress):
        """更新任务状态"""
        for i, row in enumerate(self.task_list.data):
            if row[0] == task_name:
                new_row = (task_name, status, f"{progress}%")
                self.task_list.data[i] = new_row
                break

    def update_overall_status(self, status):
        """更新整体状态"""
        self.status_value.text = status

    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.value = value
        self.progress_text.text = f"{value}%"

    def update_last_update_date(self, date_str):
        """更新最近更新日期"""
        self.update_date_value.text = date_str

    def set_button_states(self, start_enabled, pause_enabled):
        """设置按钮状态"""
        self.start_button.enabled = start_enabled
        self.pause_button.enabled = pause_enabled