from collections import namedtuple

import akshare as ak
import pandas

import hkstock
from SqliteTool import SqliteTool

# 创建对象
sqliteTool = SqliteTool()

HKFinancial = namedtuple("HKFinancial",
                     ['SECUCODE', 'SECURITY_CODE', 'SECURITY_NAME_ABBR', 'ORG_CODE', 'REPORT_DATE', 'DATE_TYPE_CODE',
                      'PER_NETCASH_OPERATE', 'PER_OI', 'BPS', 'BASIC_EPS', 'DILUTED_EPS', 'OPERATE_INCOME',
                      'OPERATE_INCOME_YOY', 'GROSS_PROFIT', 'GROSS_PROFIT_YOY', 'HOLDER_PROFIT', 'HOLDER_PROFIT_YOY',
                      'GROSS_PROFIT_RATIO', 'EPS_TTM', 'OPERATE_INCOME_QOQ', 'NET_PROFIT_RATIO', 'ROE_AVG',
                      'GROSS_PROFIT_QOQ', 'ROA', 'HOLDER_PROFIT_QOQ', 'ROE_YEARLY', 'ROIC_YEARLY', 'TAX_EBT',
                      'OCF_SALES', 'DEBT_ASSET_RATIO', 'CURRENT_RATIO', 'CURRENTDEBT_DEBT', 'START_DATE', 'FISCAL_YEAR',
                      'CURRENCY', 'IS_CNY_CODE'])


def create_table():
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
    IS_CNY_CODE int -- 是否人民币
    ); 
    """
    # 创建数据表
    sqliteTool.drop_table("drop table hk_financial;")
    sqliteTool.create_table(sql)


def fetch_from_api(code: str, indicator: str = "报告期"):
    df = ak.stock_financial_hk_analysis_indicator_em(symbol=code, indicator=indicator)
    print(df.loc[0])
    return df


def fetch_from_db(SECURITY_CODE: str, REPORT_DATE: str) -> HKFinancial:
    row = sqliteTool.query_one("select * from hk_financial where SECURITY_CODE = ? and REPORT_DATE = ?",
                               (SECURITY_CODE, REPORT_DATE))
    return HKFinancial(*row)


def delete(SECURITY_CODE: str):
    sqliteTool.delete_record(f"delete from hk_financial where SECURITY_CODE = '{SECURITY_CODE}'")


def refresh(SECURITY_CODE: str):
    rows = fetch_from_api(SECURITY_CODE)
    rows_year = fetch_from_api(SECURITY_CODE, "年度")
    rows = pandas.concat([rows, rows_year])
    rows.drop_duplicates(inplace=True)
    # 根据字典的键动态生成插入语句
    sql = ('INSERT INTO hk_financial (' + ', '.join(rows.columns.values) + ') VALUES (' +
           ', '.join(['?'] * rows.shape[1]) + ')')
    # 删除历史记录
    delete(SECURITY_CODE)
    # 执行批量插入操作
    sqliteTool.operate_many(sql, [tuple(row) for index, row in rows.iterrows()])


def refresh_all():
    rows = hkstock.fetch_all_from_db()
    for row in rows:
        refresh(row.code)
        print(row.name + " fetch finish.")


if __name__ == "__main__":
    # create_table()
    # refresh("00700")
    refresh_all()
    print(fetch_from_db("00700", "2023-12-31 00:00:00"))
