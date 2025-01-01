"""
stock filter application
"""

import toga
from stocks.hkstock import fetch_all_from_db,init_table,init_hk_stock
from toga.style import Pack
from toga.style.pack import COLUMN, ROW


class stock(toga.App):
    def startup(self):
        rows = fetch_all_from_db()
        # print(rows)
        # data = [("root%s" % i, "value %s" % i) for i in range(1, 100)]
        data = [(row.code, row.name) for row in rows]
        left_container = toga.Table(headings=["code", "name"], data=data)
        main_box = toga.Box()

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = left_container
        self.main_window.show()


def main():
    return stock()
