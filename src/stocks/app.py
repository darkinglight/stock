"""
stock filter application
"""
import toga
from toga.style.pack import COLUMN, ROW, Pack
import stocks.stocklist as stocklist


class stock(toga.App):
    def startup(self):
        stocklist.init_stock(self.paths.cache)
        stocklist.init_finance(self.paths.cache)
        table = stocklist.stock_list()
        label = toga.TextInput("abcdefg", style=Pack(flex=1))
        container = toga.OptionContainer(content=[
            ("港股", toga.Box(children=[table])),
            ("A股", toga.Box(children=[label]))
        ])
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = container
        self.main_window.show()

    def menu(self):
        def action(widget):
            self.main_window.content = stocklist.stock_list()

        things = toga.Group("Things")
        cmd0 = toga.Command(
            action,
            text="港股",
            tooltip="港股排名",
            icon="resources/icons/brutus",
            group=things,
        )
        cmd1 = toga.Command(
            action,
            text="A股",
            tooltip="A股排名",
            icon="resources/icons/cricket-72.png",
            group=things,
        )

        self.main_window.toolbar.add(cmd0, cmd1)


def main():
    return stock()
