from hs import HsSpot, HsIndicator, HsFhps, HsFinancial


def list_hs_base_info(db_path: str) -> dict:
    result = dict()
    hs_fhps_repository = HsFhps.HsFhpsRepository(db_path)
    hs_financial = HsFinancial.HsFinancialRepository(db_path)
    # get price list
    hs_spot_repository = HsSpot.HsSpotRepository(db_path)
    hs_spots = hs_spot_repository.list_low_price_10()
    for hs_spot in hs_spots:
        result[hs_spot.code] = hs_spot._asdict()
        # set bonus rate
        bonus_rate = hs_fhps_repository.get_bonus_rate(hs_spot.code)
        result[hs_spot.code]['bonus_rate'] = bonus_rate
        # set roe
        roe_entity = hs_financial.get_by_code(hs_spot.code)
        result[hs_spot.code].update(roe_entity._asdict())
    return result


if __name__ == "__main__":
    data = list_hs_base_info("finance.db")
    print(data)
