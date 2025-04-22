from collections import namedtuple

import toga
from toga.style import Pack

from hs import HsSpot, HsFhps, HsFinancial

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

def list_hs_base_info(db_path: str) -> list[HsFacade]:
    result = []
    hs_fhps_repository = HsFhps.HsFhpsRepository(db_path)
    hs_financial_repository = HsFinancial.HsFinancialRepository(db_path)
    hs_spot_repository = HsSpot.HsSpotRepository(db_path)
    hs_spots = hs_spot_repository.fetch_all_from_db()
    for hs_spot in hs_spots:
        if hs_spot.pe < 0 or hs_spot.pe > 30:
            continue
        print("start:" + hs_spot.code)
        item = hs_spot._asdict()
        # set bonus rate
        bonus_rate = hs_fhps_repository.get_bonus_rate(hs_spot.code)
        item['bonus_rate'] = bonus_rate
        # set roe
        roe_entity = hs_financial_repository.get_by_code(hs_spot.code)
        item.update(roe_entity._asdict())
        result.append(HsFacade(**item))
    return result


class HsBox(toga.Box):
    cache = dict()

    def __init__(self, data_path: str, on_active):
        self.db_file = data_path
        super().__init__(children=[self.__stock_list(on_active)])

    def __stock_list(self, on_active):
        rows = list_hs_base_info(self.db_file)
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


if __name__ == "__main__":
    data = list_hs_base_info("finance.db")
    print(data)
