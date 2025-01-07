"""
stock filter application
"""
import toga
from toga.style.pack import COLUMN, ROW, Pack
import stocks.stocklist as stocklist


class stock(toga.App):
    def startup(self):
        label = toga.TextInput("abcdefg", style=Pack(flex=1))
        container = toga.OptionContainer(content=[
            ("港股", stocklist.Stocklist(self.paths.cache, self.stock_detail)),
            ("A股", toga.Box(children=[label]))
        ])
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = container
        self.menu()
        self.main_window.show()

    def stock_detail(self, widget):
        self.main_window.content = toga.Label(text="hahaha")

    def menu(self):
        cmd = toga.Command(
            action=None,
            text="港股",
            tooltip="港股排名",
            icon="resources/icons/brutus",
        )
        self.main_window.toolbar.add(cmd)

def main():
    return stock()
