import akshare as ak

# stock_fhps_em_df = ak.stock_fhps_em(date="20231231")
# print(stock_fhps_em_df)


if __name__ == "__main__":
    # 派息
    # stock_dividend_cninfo_df = ak.stock_dividend_cninfo(symbol="002867")
    # print(stock_dividend_cninfo_df)
    # dfcf分红
    # stock_fhps_detail_em_df = ak.stock_fhps_detail_em(symbol="002867")
    # print(stock_fhps_detail_em_df)
    # tonghuashun分红
    # stock_fhps_detail_ths_df = ak.stock_fhps_detail_ths(symbol="002867")
    # print(stock_fhps_detail_ths_df)
    # 业绩预告
    # stock_yjyg_em_df = ak.stock_yjyg_em(date="20241231")
    # print(stock_yjyg_em_df)
    # 业绩快报
    # stock_yjkb_em_df = ak.stock_yjkb_em(date="20241231")
    # print(stock_yjkb_em_df)
    # A股实时行情
    # stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
    # stock_zh_a_spot_em_df = stock_zh_a_spot_em_df[stock_zh_a_spot_em_df['代码'] == '002867']
    # print(stock_zh_a_spot_em_df)
    # stock_bid_ask_em_df = ak.stock_bid_ask_em(symbol="002867")
    # print(stock_bid_ask_em_df)
    # 业绩报表
    # stock_yjbb_em_df = ak.stock_yjbb_em(date="20220331")
    # print(stock_yjbb_em_df)
    # 财务指标-同花顺
    stock_financial_abstract_ths_df = ak.stock_financial_abstract_ths(symbol="002867", indicator="按单季度")
    print(stock_financial_abstract_ths_df)
