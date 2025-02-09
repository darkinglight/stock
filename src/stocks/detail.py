import toga
from toga.style.pack import COLUMN, ROW, Pack

from stocks import hkfinancial


class Detail(toga.ScrollContainer):
    def __init__(self, db_path, code: str):
        self.db_path = db_path
        super().__init__(content=self.stock_detail(code))

    def stock_detail(self, code: str):
        detail = hkfinancial.HkFinanceRepository(self.db_path).fetch_last_year_report(code)
        main_box = toga.Box(style=Pack(direction=COLUMN))
        for key, value in detail._asdict().items():
            name_label = toga.Label(
                f"{key}: ",
                style=Pack(padding=(0, 5)),
            )
            value_label = toga.Label(
                value,
                style=Pack(flex=1),
            )
            item_box = toga.Box(style=Pack(direction=ROW, padding=5))
            item_box.add(name_label)
            item_box.add(value_label)
            main_box.add(item_box)
            # main_box.add(toga.Label(text=value))
        return main_box
