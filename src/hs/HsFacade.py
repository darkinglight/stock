from collections import namedtuple

import toga
from toga.style import Pack

from hs import HsSpot, HsFhps, HsFinancial
from hs.HsDetail import HsDetailRepository

HsFacade = namedtuple("HsFacade",
                      [
                          "code",
                          "name",
                          "pe",
                          "pb",
                          "bonus_rate",  # 分红率
                          "roe_ttm",
                          "earning_growth",
                          "debt_ratio",
                          "earning_growth_rush",  # 增速是否上扬，方便判断困境反转
                      ])

class HsBox(toga.Box):
    cache = dict()

    def __init__(self, data_path: str, on_active):
        self.db_file = data_path
        super().__init__(children=[self.__stock_list(on_active)])

    def __stock_list(self, on_active):
        hs_detail_repository = HsDetailRepository(self.db_file)
        rows = hs_detail_repository.fetch_all_from_db()
        box_data = []
        for row in rows:
            if row.bonus_rate < 0.2 or row.debt_ratio > 60:
                continue
            box_data.append((
                row.code,
                row.name,
                row.pb,
                row.pe,
                row.bonus_rate,
                row.roe_ttm,
                row.debt_ratio,
                row.earning_growth,
                row.earning_growth_rush,
                row.roe_ttm * row.bonus_rate / row.pb + row.roe_ttm * (1 - row.bonus_rate)
            ))
        # 回报率： roe * bonus_rate / pb + roe * (1 - bonus_rate)
        box_data.sort(reverse=True, key=lambda a: a[9] / a[3])
        return toga.Table(headings=["code", "name", "pb", "pe", "分红率", "年化净资产收益率(%)", "资产负债率(%)",
                                    "扣非净利润同比增长率", "扣非净利润是否加速增长"],
                          data=box_data,
                          on_select=on_active,
                          style=Pack(flex=1))
