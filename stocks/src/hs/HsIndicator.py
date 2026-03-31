from collections import namedtuple
from typing import Any

import akshare as ak

from stocks.SqliteTool import SqliteTool

HsIndicator = namedtuple("HsIndicator",
                         [
                             "code",
                             "date",
                             "roe",
                             "earning_growth",
                             "asset_growth",
                             "debt_ratio",
                         ])


class HsIndicatorRepository:

    def __init__(self, db_path: str):
        self.db_path = db_path

    def create_table(self):
        # %s#\s\+\(.*\)\s\(.*\)\s,#"\1" \2,#
        sql = """
        create table if not exists hs_indicator(
        code text,
        "日期" datetime,
        "摊薄每股收益(元)" float64,
        "加权每股收益(元)" float64,
        "每股收益_调整后(元)" float64,
        "扣除非经常性损益后的每股收益(元)" float64,
        "每股净资产_调整前(元)" float64,
        "每股净资产_调整后(元)" float64,
        "每股经营性现金流(元)" float64,
        "每股资本公积金(元)" float64,
        "每股未分配利润(元)" float64,
        "调整后的每股净资产(元)" float64,
        "总资产利润率(%)" float64,
        "主营业务利润率(%)" float64,
        "总资产净利润率(%)" float64,
        "成本费用利润率(%)" float64,
        "营业利润率(%)" float64,
        "主营业务成本率(%)" float64,
        "销售净利率(%)" float64,
        "股本报酬率(%)" float64,
        "净资产报酬率(%)" float64,
        "资产报酬率(%)" float64,
        "销售毛利率(%)" float64,
        "三项费用比重" float64,
        "非主营比重" float64,
        "主营利润比重" float64,
        "股息发放率(%)" float64,
        "投资收益率(%)" float64,
        "主营业务利润(元)" float64,
        "净资产收益率(%)" float64,
        "加权净资产收益率(%)" float64,
        "扣除非经常性损益后的净利润(元)" float64,
        "主营业务收入增长率(%)" float64,
        "净利润增长率(%)" float64,
        "净资产增长率(%)" float64,
        "总资产增长率(%)" float64,
        "应收账款周转率(次)" float64,
        "应收账款周转天数(天)" float64,
        "存货周转天数(天)" float64,
        "存货周转率(次)" float64,
        "固定资产周转率(次)" float64,
        "总资产周转率(次)" float64,
        "总资产周转天数(天)" float64,
        "流动资产周转率(次)" float64,
        "流动资产周转天数(天)" float64,
        "股东权益周转率(次)" float64,
        "流动比率" float64,
        "速动比率" float64,
        "现金比率(%)" float64,
        "利息支付倍数" float64,
        "长期债务与营运资金比率(%)" float64,
        "股东权益比率(%)" float64,
        "长期负债比率(%)" float64,
        "股东权益与固定资产比率(%)" float64,
        "负债与所有者权益比率(%)" float64,
        "长期资产与长期资金比率(%)" float64,
        "资本化比率(%)" float64,
        "固定资产净值率(%)" float64,
        "资本固定化比率(%)" float64,
        "产权比率(%)" float64,
        "清算价值比率(%)" float64,
        "固定资产比重(%)" float64,
        "资产负债率(%)" float64,
        "总资产(元)" float64,
        "经营现金净流量对销售收入比率(%)" float64,
        "资产的经营现金流量回报率(%)" float64,
        "经营现金净流量与净利润的比率(%)" float64,
        "经营现金净流量对负债比率(%)" float64,
        "现金流量比率(%)" float64,
        "短期股票投资(元)" float64,
        "短期债券投资(元)" float64,
        "短期其它经营性投资(元)" float64,
        "长期股票投资(元)" float64,
        "长期债券投资(元)" float64,
        "长期其它经营性投资(元)" float64,
        "1年以内应收帐款(元)" float64,
        "1-2年以内应收帐款(元)" float64,
        "2-3年以内应收帐款(元)" float64,
        "3年以内应收帐款(元)" float64,
        "1年以内预付货款(元)" float64,
        "1-2年以内预付货款(元)" float64,
        "2-3年以内预付货款(元)" float64,
        "3年以内预付货款(元)" float64,
        "1年以内其它应收款(元)" float64,
        "1-2年以内其它应收款(元)" float64,
        "2-3年以内其它应收款(元)" float64,
        "3年以内其它应收款(元)" float64
        ); 
        """
        sqlite_tool = SqliteTool(self.db_path)
        # 创建数据表
        sqlite_tool.drop_table("drop table hs_indicator;")
        sqlite_tool.create_table(sql)
        sqlite_tool.close_con()

    def fetch_from_api(self, code: str, start_year="2020"):
        df = ak.stock_financial_analysis_indicator(symbol=code, start_year=start_year)
        return df

    def fetch_from_db(self, code: str, date: str):
        sqlite_tool = SqliteTool(self.db_path)
        row = sqlite_tool.query_one('select "code", "日期", "净资产收益率(%)", "净利润增长率(%)", "净资产增长率(%)", "资产负债率(%)" '
                                    'from hs_indicator where code = ? and "日期" = ?', (code, date))
        sqlite_tool.close_con()
        return HsIndicator(*row)

    def list_from_db(self, code: str):
        sqlite_tool = SqliteTool(self.db_path)
        rows = sqlite_tool.query_many('select "code", "日期", "净资产收益率(%)", "净利润增长率(%)", "净资产增长率(%)", "资产负债率(%)" '
                                      'from hs_indicator where code = ?', (code,))
        sqlite_tool.close_con()
        if not rows:
            return []
        return [HsIndicator(*row) for row in rows]

    def list_last_year_report(self) -> list[Any] | list[HsIndicator]:
        sqlite_tool = SqliteTool(self.db_path)
        rows = sqlite_tool.query_many('select "code", "日期", "净资产收益率(%)", "净利润增长率(%)", "净资产增长率(%)", "资产负债率(%)" '
                                      'from (SELECT * FROM hs_indicator where 日期 like "%-12-31" ORDER BY 日期 DESC) '
                                      'GROUP BY code')
        sqlite_tool.close_con()
        if not rows:
            return []
        return [HsIndicator(*row) for row in rows]

    def delete(self, code: str):
        sqlite_tool = SqliteTool(self.db_path)
        sqlite_tool.delete_record(f"delete from hs_indicator where code = '{code}'")
        sqlite_tool.close_con()

    def refresh(self, code: str, start_year="2020"):
        rows = self.fetch_from_api(code, start_year)
        # 根据字典的键动态生成插入语句
        sql = ('INSERT INTO hs_indicator ("code", "' + '", "'.join(rows.columns.values) + '") VALUES (?, ' +
               ', '.join(['?'] * rows.shape[1]) + ')')
        # 删除历史记录
        self.delete(code)
        # 执行批量插入操作
        sqlite_tool = SqliteTool(self.db_path)
        sqlite_tool.operate_many(sql, [(code,) + tuple(row) for index, row in rows.iterrows()])
        sqlite_tool.close_con()

    def refresh_all(self, codes: tuple, start_year="2020"):
        for code in codes:
            self.refresh(code, start_year)
            print(code, "finish")


if __name__ == "__main__":
    repository = HsIndicatorRepository("finance.db")
    # repository.create_table()
    # repository.refresh("002867", "2023")
    # for item in repository.list_from_db("002867"):
    #     print(item.日期, item.净资产收益率, item.净资产报酬率, item.加权每股收益, item.股息发放率)
    for item in repository.list_last_year_report():
        print(item)
