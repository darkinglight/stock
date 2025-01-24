from collections import namedtuple
from typing import Any

import akshare as ak

from stocks.SqliteTool import SqliteTool

HsFinancial = namedtuple("HsFinancial",
                         [
                             "code",
                             "date",
                             "roe",
                             "earning_growth",
                             "debt_ratio",
                         ])


class HsFinancialRepository:

    def __init__(self, db_path: str):
        self.db_path = db_path

    def create_table(self):
        # %s#\s\+\(.*\)\s\(.*\)\s,#"\1" \2,#
        sql = """
        create table if not exists hs_financial(
        code text,
        "报告期" text,
        "净利润" text,
        "净利润同比增长率" text,
        "扣非净利润" text,
        "扣非净利润同比增长率" text,
        "营业总收入" text,
        "营业总收入同比增长率" text,
        "基本每股收益" text,
        "每股净资产" text,
        "每股资本公积金" text,
        "每股未分配利润" text,
        "每股经营现金流" text,
        "销售净利率" text,
        "销售毛利率" text,
        "净资产收益率" text,
        "净资产收益率-摊薄" text,
        "营业周期" text,
        "存货周转率" text,
        "存货周转天数" text,
        "应收账款周转天数" text,
        "流动比率" text,
        "速动比率" text,
        "保守速动比率" text,
        "产权比率" text,
        "资产负债率" text
        ); 
        """
        sqlite_tool = SqliteTool(self.db_path)
        # 创建数据表
        sqlite_tool.drop_table("drop table hs_financial;")
        sqlite_tool.create_table(sql)
        sqlite_tool.close_con()

    # financial: ["按报告期", "按年度", "按单季度"]
    def fetch_from_api(self, code: str, financial="按单季度"):
        df = ak.stock_financial_abstract_ths(symbol=code, indicator=financial)
        return df

    def fetch_from_db(self, code: str, date: str):
        sqlite_tool = SqliteTool(self.db_path)
        row = sqlite_tool.query_one('select "code", "报告期", "净资产收益率", "净利润同比增长率", "资产负债率" '
                                    'from hs_financial where code = ? and "报告期" = ?', (code, date))
        sqlite_tool.close_con()
        return HsFinancial(*row)

    def list_from_db(self, code: str):
        sqlite_tool = SqliteTool(self.db_path)
        rows = sqlite_tool.query_many('select "code", "报告期", "净资产收益率", "净利润同比增长率", "资产负债率" '
                                      'from hs_financial where code = ?', (code,))
        sqlite_tool.close_con()
        if not rows:
            return []
        return [HsFinancial(*row) for row in rows]

    def list_last_year_report(self) -> list[Any] | list[HsFinancial]:
        sqlite_tool = SqliteTool(self.db_path)
        sql = """
        WITH RankedData AS (
            SELECT
                *,
                ROW_NUMBER() OVER (PARTITION BY code ORDER BY 报告期 DESC) AS row_num
            FROM
                hs_financial
        )
        SELECT 
            "code", 
            "报告期", 
            SUM(CAST("净资产收益率" AS REAL)), 
            CAST("净利润同比增长率" AS REAL), 
            CAST("资产负债率" AS REAL)
        FROM
            RankedData
        WHERE
            row_num <= 4
        GROUP BY
            code
        """
        rows = sqlite_tool.query_many(sql)
        sqlite_tool.close_con()
        if not rows:
            return []
        return [HsFinancial(*row) for row in rows]

    def delete(self, code: str):
        sqlite_tool = SqliteTool(self.db_path)
        sqlite_tool.delete_record(f"delete from hs_financial where code = '{code}'")
        sqlite_tool.close_con()

    def refresh(self, code: str):
        rows = self.fetch_from_api(code)
        # 根据字典的键动态生成插入语句
        sql = ('INSERT INTO hs_financial ("code", "' + '", "'.join(rows.columns.values) + '") VALUES (?, ' +
               ', '.join(['?'] * rows.shape[1]) + ')')
        # 删除历史记录
        self.delete(code)
        # 执行批量插入操作
        sqlite_tool = SqliteTool(self.db_path)
        sqlite_tool.operate_many(sql, [(code,) + tuple(row) for index, row in rows.iterrows() if row['报告期'] >= '2020-01-01'])
        sqlite_tool.close_con()

    def refresh_all(self, codes: tuple):
        for code in codes:
            self.refresh(code)
            print(code, "finish")


if __name__ == "__main__":
    repository = HsFinancialRepository("finance.db")
    # repository.create_table()
    # repository.refresh("002867")
    # for item in repository.list_from_db("002867"):
    #     print(item)
    for item in repository.list_last_year_report():
        print(item)
