"""
stock filter application
"""
import toga
from toga.style.pack import COLUMN, ROW, Pack
import stocks.stocklist as stocklist
from stocks import hkstock


class stock(toga.App):
    def startup(self):
        stocklist.init_stock(self.paths.cache)
        stocklist.init_finance(self.paths.cache)
        table = self.stock_list()
        label = toga.TextInput("abcdefg", style=Pack(flex=1))
        container = toga.OptionContainer(content=[
            ("港股", toga.Box(children=[table])),
            ("A股", toga.Box(children=[label]))
        ])
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = container
        self.main_window.show()

    def stock_list(self):
        def stock_detail(widget):
            print(widget)
            self.main_window.content = toga.Box()

        rows = hkstock.fetch_all_from_db()
        # data = [("root%s" % i, "value %s" % i) for i in range(1, 100)]
        data = [(row.code, row.name) for row in rows]
        return toga.Table(headings=["code", "name"],
                          data=data,
                          on_select=stock_detail,
                          style=Pack(flex=1))



def main():
    return stock()
