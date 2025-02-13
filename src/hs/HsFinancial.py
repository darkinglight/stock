from collections import namedtuple
from typing import Any

import akshare as ak

from stocks.SqliteTool import SqliteTool

# todo 根据财报更新
HsFinancial = namedtuple("HsFinancial",
                         [
                             "code",
                             "roe_ttm",
                             "earning_growth",
                             "debt_ratio",
                             "earning_growth_rush",  # 增速是否上扬，方便判断困境反转
                         ])


class HsFinancialRepository:

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.data = {}
        for entity in self.__list_last_year_report():
            self.data[entity.code] = entity

    def init_table(self):
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
        sqlite_tool.create_table(sql)
        sqlite_tool.close_con()

    # financial: ["按报告期", "按年度", "按单季度"]
    def __fetch_from_api(self, code: str, financial="按单季度"):
        df = ak.stock_financial_abstract_ths(symbol=code, indicator=financial)
        return df

    def __get_report(self, code: str) -> HsFinancial:
        sql = f"""
        SELECT
            code,
            CAST("净资产收益率" AS REAL), 
            CAST("净利润同比增长率" AS REAL), 
            CAST("资产负债率" AS REAL)
        FROM
            hs_financial
        WHERE
            code = '{code}'
        ORDER BY
            "报告期" DESC
        LIMIT 4
        """
        sqlite_tool = SqliteTool(self.db_path)
        rows = sqlite_tool.query_many(sql)
        sqlite_tool.close_con()
        roe_ttm = round(sum(row[1] for row in rows), 2)
        growth_rush = rows[0][2] > rows[1][2] > rows[2][2]
        result = HsFinancial(code, roe_ttm, rows[0][2], rows[0][3], growth_rush)
        return result

    def __list_last_year_report(self) -> list[Any] | list[HsFinancial]:
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
            ROUND(SUM(CAST("净资产收益率" AS REAL)), 2), 
            CAST("净利润同比增长率" AS REAL), 
            CAST("资产负债率" AS REAL),
            ""
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

    def __delete(self, code: str):
        sqlite_tool = SqliteTool(self.db_path)
        sqlite_tool.delete_record(f"delete from hs_financial where code = '{code}'")
        sqlite_tool.close_con()

    def __refresh(self, code: str):
        rows = self.__fetch_from_api(code)
        # 根据字典的键动态生成插入语句
        sql = ('INSERT INTO hs_financial ("code", "' + '", "'.join(rows.columns.values) + '") VALUES (?, ' +
               ', '.join(['?'] * rows.shape[1]) + ')')
        sqlite_tool = SqliteTool(self.db_path)
        # 删除历史记录
        self.__delete(code)
        # 执行批量插入操作
        sqlite_tool.operate_many(sql, [(code,) + tuple(row) for index, row in rows.iterrows() if
                                       row['报告期'] >= '2020-01-01'])
        sqlite_tool.close_con()

    def get_by_code(self, code: str) -> HsFinancial:
        if self.data.get(code) is None:
            self.__refresh(code)
            self.data[code] = self.__get_report(code)
        return self.data[code]


if __name__ == "__main__":
    repository = HsFinancialRepository("finance.db")
    repository.init_table()
    # repository.refresh("002867")
    print(repository.get_by_code("601299"))
