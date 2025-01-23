from hs import HsSpot, HsIndicator, HsFhps


def list_hs_base_info(db_path: str) -> dict:
    result = dict()
    # get price list
    hs_spot_repository = HsSpot.HsSpotRepository(db_path)
    hs_spots = hs_spot_repository.fetch_all_from_db()
    for hs_spot in hs_spots:
        result[hs_spot.code] = hs_spot._asdict()
    # get roe
    hs_indicator_repository = HsIndicator.HsIndicatorRepository(db_path)
    hs_indicators = hs_indicator_repository.list_last_year_report()
    # get bonus
    hs_fhps_repository = HsFhps.HsFhpsRepository(db_path)
    hs_fhps_list = hs_fhps_repository.list_bonus_rate()
    for hs_fhps in hs_fhps_list:
        result[hs_fhps.code].update(hs_fhps._asdict())
    return result


if __name__ == "__main__":
    data = list_hs_base_info("finance.db")
    print(data["002867"])
