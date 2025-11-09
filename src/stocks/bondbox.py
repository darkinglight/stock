from pathlib import Path

import toga
from toga.style import Pack

from hs.HsDetail import HsDetailRepository
from stocks.bond import BondRepository


class BondBox(toga.Box):
    def __init__(self, data_path: Path, on_active):
        self.db_file = data_path
        super().__init__(children=[self.stock_list(on_active)])

    def stock_list(self, on_active):
        bond_repository = BondRepository(self.db_file)
        rows = bond_repository.fetch_all_from_db()
        hs_detail_repository = HsDetailRepository(self.db_file)
        box_data = []
        for row in rows:
            try:
                # 尝试将 bond_price 转换为浮点数
                bond_price = float(row.bond_price) if row.bond_price is not None else 1000
            except ValueError:
                # 转换失败，将 bond_price 设为 None
                bond_price = 1000
            if bond_price > 150:
                continue
            stock_detail = hs_detail_repository.fetch_one_from_db(row.stock_code)
            if stock_detail is None:
                continue
            roe_ttm = stock_detail.roe_ttm if stock_detail.roe_ttm is not None else 0
            debt_ratio = stock_detail.debt_ratio if stock_detail.debt_ratio is not None else 100
            if roe_ttm < 5 or debt_ratio > 60:
                continue
            box_data.append((
                row.bond_code,
                row.bond_name,
                row.bond_price,
                row.bond_over_percent,
                row.stock_over_percent,
                stock_detail.roe_ttm,
                stock_detail.debt_ratio
            ))
        box_data.sort(reverse=False, key=lambda a: a[2])
        return toga.Table(headings=["转债代码", "转债名称", "转债最新价", "纯债溢价率", "转股溢价率", "年化净资产收益率(%)", "资产负债率(%)"],
                          data=box_data,
                          on_select=on_active,
                          style=Pack(flex=1))


if __name__ == "__main__":
    repository = BondRepository()
    repository.init_table()
    repository.refresh()
