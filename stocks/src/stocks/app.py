"""
stock select application - scroll load debug
"""

import asyncio

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW


class stocks(toga.App):
    def startup(self):
        self.current_page = 1
        self.total_stocks = 300
        self.loading = False

        self.content_box = toga.Box(style=Pack(direction=COLUMN))

        self.scroll_container = toga.ScrollContainer(
            content=self.content_box,
            style=Pack(flex=1),
            horizontal=False,
            vertical=True,
            on_scroll=self.on_scroll
        )

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.scroll_container
        self.main_window.show()

        asyncio.create_task(self.load_stock_data())

    async def load_stock_data(self, refresh=False, restore_pos=None):
        if self.loading:
            return
        self.loading = True

        if refresh:
            self.current_page = 1
            self.content_box.clear()

        start = (self.current_page - 1) * 10 + 1
        end = min(start + 9, self.total_stocks)
        if start > self.total_stocks:
            self.loading = False
            return

        await asyncio.sleep(0.5)

        for i in range(start, end + 1):
            row = toga.Box(style=Pack(direction=ROW, padding=5))
            title = toga.Label(f"股票{i:04d}", style=Pack(width=100, padding_left=5))
            subtitle = toga.Label(f"价格: {10 + i % 30:.2f}", style=Pack(padding_left=10))
            row.add(title)
            row.add(subtitle)
            self.content_box.add(row)

        self.current_page += 1
        self.loading = False

        if restore_pos is not None:
            self.scroll_container.vertical_position = restore_pos

        print(f"[DEBUG] loaded {start}-{end}, children={len(self.content_box.children)}")

    def on_scroll(self, widget, **kwargs):
        if self.loading:
            return
        if len(self.content_box.children) >= self.total_stocks:
            return

        current_pos = widget.vertical_position
        max_pos = widget.max_vertical_position

        print(f"[DEBUG] on_scroll fired, pos={current_pos}, max={max_pos}")

        if max_pos > 0 and (max_pos - current_pos) < 100:
            asyncio.create_task(self.load_stock_data(restore_pos=current_pos))

    def on_refresh(self, widget, **kwargs):
        asyncio.create_task(self.load_stock_data(refresh=True))


def main():
    return stocks()
