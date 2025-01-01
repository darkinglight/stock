from collections import namedtuple

import akshare as ak
import pandas

from SqliteTool import SqliteTool
import hkstock

# 创建对象
sqliteTool = SqliteTool()

HKReport = namedtuple("HKReport", ['SECUCODE', 'SECURITY_CODE', 'SECURITY_NAME_ABBR', 'ORG_CODE',
                                   'REPORT_DATE', 'DATE_TYPE_CODE', 'FISCAL_YEAR', 'STD_ITEM_CODE',
                                   'STD_ITEM_NAME', 'AMOUNT', 'STD_REPORT_DATE'])


def init_table():
    # 创建数据表info的SQL语句
    sql = """
    create table if not exists hk_report(
    SECUCODE TEXT, -- 带后缀股票代码 
    SECURITY_CODE TEXT, -- 不带后缀股票代码 
    SECURITY_NAME_ABBR TEXT, -- 股票名称 
    ORG_CODE TEXT, -- 组织代码 
    REPORT_DATE TEXT, -- 报告期
    DATE_TYPE_CODE TEXT, -- 数据类型
    FISCAL_YEAR TEXT, -- 财年
    STD_ITEM_CODE TEXT, -- code
    STD_ITEM_NAME TEXT, -- name
    AMOUNT TEXT, -- amount
    START_DATE TEXT, -- 报告期
    STD_REPORT_DATE TEXT -- 报告期
    );
    """
    # 删除表
    sqliteTool.drop_table("drop table hk_report;")
    # 创建数据表
    sqliteTool.create_table(sql)


def delete(SECURITY_CODE: str):
    sqliteTool.delete_record(f"delete from hk_report where SECURITY_CODE = '{SECURITY_CODE}'")


def fetch_from_api(stock, symbol, indicator):
    df = ak.stock_financial_hk_report_em(stock=stock, symbol=symbol, indicator=indicator)
    return df


def refresh(stock):
    # "资产负债表", "利润表", "现金流量表"
    rows = fetch_from_api(stock, "资产负债表", "年度")
    rows_cash = fetch_from_api(stock, "现金流量表", "年度")
    rows_earning = fetch_from_api(stock, "现金流量表", "年度")
    rows = pandas.concat([rows, rows_cash, rows_earning])
    rows.drop_duplicates(inplace=True)
    rows = rows[rows["REPORT_DATE"] > "2019-12-31 00:00:00"]
    # 根据字典的键动态生成插入语句
    sql = ('INSERT INTO hk_report (' + ', '.join(rows.columns.values) + ') VALUES (' +
           ', '.join(['?'] * rows.shape[1]) + ')')
    # 删除历史记录
    delete(stock)
    # 执行批量插入操作
    sqliteTool.operate_many(sql, [tuple(row) for index, row in rows.iterrows()])


def refresh_all():
    rows = hkstock.fetch_all_from_db()
    for row in rows:
        refresh(row.code)
        print(row.name + " fetch finish.")


if __name__ == "__main__":
    init_table()
    refresh_all()
