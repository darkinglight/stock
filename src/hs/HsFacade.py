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


def list_hs_base_info(db_path: str) -> list:
    result = []
    hs_fhps_repository = HsFhps.HsFhpsRepository(db_path)
    hs_financial = HsFinancial.HsFinancialRepository(db_path)
    # get price list
    hs_spot_repository = HsSpot.HsSpotRepository(db_path)
    hs_spots = hs_spot_repository.list_low_price_10()
    for hs_spot in hs_spots:
        item = hs_spot._asdict()
        # set bonus rate
        bonus_rate = hs_fhps_repository.get_bonus_rate(hs_spot.code)
        item['bonus_rate'] = bonus_rate
        # set roe
        roe_entity = hs_financial.get_by_code(hs_spot.code)
        item.update(roe_entity._asdict())
        result.append(HsFacade(**item))
    return result


class HsBox(toga.Box):
    cache = dict()

    def __init__(self, data_path: str, on_active):
        self.db_file = data_path
        super().__init__(children=[self.__stock_list(on_active)])

    def __stock_list(self, on_active):
        rows = HsFacade.list_hs_base_info(self.db_file)
        data = []
        for row in rows.values():
            data.append((
                row.code,
                row.name,
            ))
        data.sort(key=lambda a: a[3] / a[4])
        return toga.Table(headings=["code", "name", "pb", "pe", "年化净资产收益率(%)", "资产负债率(%)"],
                          data=data,
                          on_select=on_active,
                          style=Pack(flex=1))


if __name__ == "__main__":
    data = list_hs_base_info("finance.db")
    print(data)
