import datetime
from collections import namedtuple
from typing import Any

import akshare as ak
import pandas

from stocks import hkstock
from stocks.SqliteTool import SqliteTool

# 创建对象

HKFinancial = namedtuple("HKFinancial",
                         ['SECUCODE', 'SECURITY_CODE', 'SECURITY_NAME_ABBR', 'ORG_CODE', 'REPORT_DATE',
                          'DATE_TYPE_CODE',
                          'PER_NETCASH_OPERATE', 'PER_OI', 'BPS', 'BASIC_EPS', 'DILUTED_EPS', 'OPERATE_INCOME',
                          'OPERATE_INCOME_YOY', 'GROSS_PROFIT', 'GROSS_PROFIT_YOY', 'HOLDER_PROFIT',
                          'HOLDER_PROFIT_YOY',
                          'GROSS_PROFIT_RATIO', 'EPS_TTM', 'OPERATE_INCOME_QOQ', 'NET_PROFIT_RATIO', 'ROE_AVG',
                          'GROSS_PROFIT_QOQ', 'ROA', 'HOLDER_PROFIT_QOQ', 'ROE_YEARLY', 'ROIC_YEARLY', 'TAX_EBT',
                          'OCF_SALES', 'DEBT_ASSET_RATIO', 'CURRENT_RATIO', 'CURRENTDEBT_DEBT', 'START_DATE',
                          'FISCAL_YEAR',
                          'CURRENCY', 'IS_CNY_CODE',
                          'UPDATE_AT'])


class HkFinanceRepository:

    def __init__(self, db_path: str = 'finance.db'):
        self.db_path = db_path

    def create_table(self):
        sql = """
        create table if not exists hk_financial(
        SECUCODE text, -- 带后缀股票代码
        SECURITY_CODE text, -- 不带后缀股票代码
        SECURITY_NAME_ABBR text, -- 股票名称
        ORG_CODE text, -- 组织代码
        REPORT_DATE text, -- 报告期
        DATE_TYPE_CODE text, -- 数据类型
        PER_NETCASH_OPERATE float, -- 每股经营现金流(元)
        PER_OI float, -- 每股营业收入(元)
        BPS float, -- 每股净资产(元)
        BASIC_EPS float, -- 基本每股收益(元)
        DILUTED_EPS float, -- 稀释每股收益(元)
        OPERATE_INCOME float, -- 营业总收入(元)
        OPERATE_INCOME_YOY float, -- 营业总收入同比增长(%)
        GROSS_PROFIT float, -- 毛利润(元)
        GROSS_PROFIT_YOY float, -- 毛利润同比增长(%)
        HOLDER_PROFIT float, -- 归母净利润(元)
        HOLDER_PROFIT_YOY float, -- 归母净利润同比增长(%)
        GROSS_PROFIT_RATIO float, -- 毛利率(%)
        EPS_TTM float, -- TTM每股收益(元)
        OPERATE_INCOME_QOQ float, -- 营业总收入滚动环比增长(%)
        NET_PROFIT_RATIO float, -- 净利率(%)
        ROE_AVG float, -- 平均净资产收益率(%)
        GROSS_PROFIT_QOQ float, -- 毛利润滚动环比增长(%)
        ROA float, -- 总资产净利率(%)
        HOLDER_PROFIT_QOQ float, -- 归母净利润滚动环比增长(%)
        ROE_YEARLY float, -- 年化净资产收益率(%)
        ROIC_YEARLY float, -- 年化投资回报率(%)
        TAX_EBT float, -- 所得税/利润总额(%)
        OCF_SALES float, -- 经营现金流/营业收入(%)
        DEBT_ASSET_RATIO float, -- 资产负债率(%)
        CURRENT_RATIO float, -- 流动比率(倍)
        CURRENTDEBT_DEBT float, -- 流动负债/总负债(%)
        START_DATE text, -- 起始日期
        FISCAL_YEAR text, -- 最后日期
        CURRENCY text, -- 币种
        IS_CNY_CODE int, -- 是否人民币
        UPDATE_AT text -- 最后更新日期
        ); 
        """
        sqlite_tool = SqliteTool(self.db_path)
        # 创建数据表
        sqlite_tool.create_table(sql)
        sqlite_tool.close_con()

    def drop_table(self):
        sqlite_tool = SqliteTool(self.db_path)
        sqlite_tool.drop_table("drop table hk_financial;")
        sqlite_tool.close_con()

    def fetch_from_api(self, code: str, indicator: str = "报告期"):
        df = ak.stock_financial_hk_analysis_indicator_em(symbol=code, indicator=indicator)
        return df

    def fetch_from_db(self, SECURITY_CODE: str, REPORT_DATE: str) -> HKFinancial:
        sqlite_tool = SqliteTool(self.db_path)
        row = sqlite_tool.query_one("select * from hk_financial where SECURITY_CODE = ? and REPORT_DATE = ?",
                                    (SECURITY_CODE, REPORT_DATE))
        sqlite_tool.close_con()
        return HKFinancial(*row)

    def fetch_last_3year_report(self, SECURITY_CODE: str):
        sqlite_tool = SqliteTool(self.db_path)
        rows = sqlite_tool.query_many("select * from hk_financial "
                                      f"where SECURITY_CODE = '{SECURITY_CODE}' and DATE_TYPE_CODE = '001' "
                                      "order by REPORT_DATE DESC "
                                      "limit 3")
        sqlite_tool.close_con()
        if not rows:
            return []
        return [HKFinancial(*row) for row in rows]

    def fetch_last_year_report(self, SECURITY_CODE: str) -> HKFinancial:
        sqlite_tool = SqliteTool(self.db_path)
        row = sqlite_tool.query_one("select * from hk_financial "
                                   f"where SECURITY_CODE = '{SECURITY_CODE}' and DATE_TYPE_CODE = '001' "
                                   "order by REPORT_DATE DESC "
                                   "limit 1")
        sqlite_tool.close_con()
        return HKFinancial(*row)

    def list_last_year_report(self) -> list[Any] | list[HKFinancial]:
        sqlite_tool = SqliteTool(self.db_path)
        rows = sqlite_tool.query_many("select * from "
                                     "(SELECT * FROM hk_financial WHERE DATE_TYPE_CODE = '001' ORDER BY REPORT_DATE DESC) "
                                     "GROUP BY SECURITY_CODE")
        sqlite_tool.close_con()
        if not rows:
            return []
        return [HKFinancial(*row) for row in rows]

    def delete(self, SECURITY_CODE: str):
        sqlite_tool = SqliteTool(self.db_path)
        sqlite_tool.delete_record(f"delete from hk_financial where SECURITY_CODE = '{SECURITY_CODE}'")
        sqlite_tool.close_con()

    def refresh(self, SECURITY_CODE: str):
        rows = self.fetch_from_api(SECURITY_CODE)
        rows_year = self.fetch_from_api(SECURITY_CODE, "年度")
        rows = pandas.concat([rows, rows_year])
        rows.drop_duplicates(inplace=True)
        rows['UPDATE_AT'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # 根据字典的键动态生成插入语句
        sql = ('INSERT INTO hk_financial (' + ', '.join(rows.columns.values) + ') VALUES (' +
               ', '.join(['?'] * rows.shape[1]) + ')')
        # 删除历史记录
        self.delete(SECURITY_CODE)
        # 执行批量插入操作
        sqlite_tool = SqliteTool(self.db_path)
        sqlite_tool.operate_many(sql, [tuple(row) for index, row in rows.iterrows()])
        sqlite_tool.close_con()

    def refresh_all(self):
        time_map = self.code_time_map()
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        rows = hkstock.HkStockRepository(self.db_path).fetch_all_from_db()
        for row in rows:
            update_at = time_map.get(row.code)
            if update_at and update_at.startswith(today):
                print(f"{row.name} 的数据今日已更新，跳过。")
                continue
            self.refresh(row.code)
            print(row.name + " fetch finish.")

    def code_time_map(self) -> dict[str, str]:
        # 获取当前记录的map[ 'SECURITY_CODE',  -> UPDATE_AT]
        sqlite_tool = SqliteTool(self.db_path)
        rows = sqlite_tool.query_many("select SECURITY_CODE, UPDATE_AT from hk_financial")
        sqlite_tool.close_con()
        return {row[0]: row[1] for row in rows}


if __name__ == "__main__":
    repository = HkFinanceRepository()
    # repository.drop_table()
    # repository.create_table()
    # repository.refresh("00700")
    repository.refresh_all()
    print(HkFinanceRepository().list_last_year_report())
