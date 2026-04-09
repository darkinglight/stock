from typing import Optional, Callable, Dict

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER


class TaskRow(toga.Box):
    """单个任务行，包含名称、状态、进度和控制按钮"""

    def __init__(
        self,
        task_name: str,
        on_start: Optional[Callable] = None,
        on_pause: Optional[Callable] = None,
    ):
        super().__init__(style=Pack(direction=ROW, margin=5, alignment=CENTER))

        self.task_name = task_name
        self._on_start_handler = on_start
        self._on_pause_handler = on_pause
        self._is_running = False

        self.name_label = toga.Label(
            task_name, style=Pack(width=120, font_weight="bold")
        )

        self.status_label = toga.Label("就绪", style=Pack(width=80))

        self.progress_label = toga.Label("0%", style=Pack(width=60))

        self.start_button = toga.Button(
            "开始",
            on_press=self._on_start,
            style=Pack(width=80, margin_left=10),
        )

        self.pause_button = toga.Button(
            "暂停",
            on_press=self._on_pause,
            style=Pack(width=80, margin_left=5),
            enabled=False,
        )

        self.add(self.name_label)
        self.add(self.status_label)
        self.add(self.progress_label)
        self.add(self.start_button)
        self.add(self.pause_button)

    def _on_start(self, widget):
        if self._on_start_handler:
            self._on_start_handler(self.task_name)

    def _on_pause(self, widget):
        if self._on_pause_handler:
            self._on_pause_handler(self.task_name)

    def update_status(self, status: str, progress: float):
        self.status_label.text = status
        self.progress_label.text = f"{progress:.2f}%"

    def set_running(self, running: bool):
        self._is_running = running
        self.start_button.enabled = not running
        self.pause_button.enabled = running


class StockTaskView(toga.Box):

    def __init__(
        self,
        on_start_update: Optional[Callable] = None,
        on_pause_update: Optional[Callable] = None,
    ):
        self._on_start_update_handler = on_start_update
        self._on_pause_update_handler = on_pause_update

        super().__init__(style=Pack(flex=1, direction=COLUMN, margin=10))

        self.title = toga.Label(
            "任务管理", style=Pack(font_size=18, font_weight="bold", margin_bottom=10)
        )
        self.add(self.title)

        header_box = toga.Box(style=Pack(direction=ROW, margin=5, alignment=CENTER))
        header_box.add(toga.Label("任务名称", style=Pack(width=120, font_weight="bold")))
        header_box.add(toga.Label("状态", style=Pack(width=80, font_weight="bold")))
        header_box.add(toga.Label("进度", style=Pack(width=60, font_weight="bold")))
        header_box.add(toga.Label("", style=Pack(width=170)))
        self.add(header_box)

        self.task_rows: Dict[str, TaskRow] = {}
        tasks = ["Stock刷新", "Financial更新", "Bonus更新"]

        for task_name in tasks:
            row = TaskRow(
                task_name=task_name,
                on_start=self._on_task_start,
                on_pause=self._on_task_pause,
            )
            self.task_rows[task_name] = row
            self.add(row)

    def _on_task_start(self, task_name: str):
        if self._on_start_update_handler:
            self._on_start_update_handler(task_name)

    def _on_task_pause(self, task_name: str):
        if self._on_pause_update_handler:
            self._on_pause_update_handler(task_name)

    def update_task_status(self, task_name: str, status: str, progress: float):
        if task_name in self.task_rows:
            self.task_rows[task_name].update_status(status, progress)

    def update_overall_status(self, status: str):
        pass

    def update_progress(self, value: int):
        pass

    def set_button_states(self, start_enabled: bool, pause_enabled: bool):
        pass

    def set_task_running(self, task_name: str, running: bool):
        if task_name in self.task_rows:
            self.task_rows[task_name].set_running(running)
