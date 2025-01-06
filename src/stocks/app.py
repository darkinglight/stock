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
            ("港股", stocklist.Stocklist(self.paths.cache)),
            ("A股", toga.Box(children=[label]))
        ])
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = container
        self.main_window.show()


def main():
    return stock()
