"""
stock filter application
"""

import toga
from stocks.stocklist import stock_list
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER, BOTTOM


class stock(toga.App):
    box = toga.Box(style=Pack(direction=COLUMN, alignment=BOTTOM, padding=10))

    def startup(self):
        main_box = toga.Box()
        main_box.add(self.nav())
        main_box.add(self.box)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

    def nav(self):
        def page_one(widget):
            self.box.clear()
            self.box.add(stock_list())

        def page_two(widget):
            self.box.clear()
            self.box.add(toga.TextInput(value='page two.'))

        def page_three(widget):
            self.box.clear()
            self.box.add(toga.TextInput(value='page three.'))

        nav_box = toga.Box(style=Pack(direction=ROW, alignment=CENTER, padding=(0, 10)))
        icon_style = Pack(width=24)
        nav_button_one = toga.Button('🏠', on_press=page_one, style=icon_style)
        nav_box.add(nav_button_one)
        nav_button_two = toga.Button('📚', on_press=page_two, style=icon_style)
        nav_box.add(nav_button_two)
        nav_button_three = toga.Button('🛠️', on_press=page_three, style=icon_style)
        nav_box.add(nav_button_three)
        return nav_box






def main():
    return stock()
