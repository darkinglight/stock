import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Optional, Callable, Dict
import datetime
import pandas as pd
from models.hk_financial import HkFinancial
from models.stock import Stock
from database.connection import DatabaseConnectionManager
from services.hk_stock_service import HkStockService
import akshare as ak


class HkFinancialService:
    """港股财务数据服务"""

    SQL_CREATE_HK_FINANCIAL_TABLE = '''
    CREATE TABLE IF NOT EXISTS hk_financial (
        SECUCODE TEXT,
        SECURITY_CODE TEXT,
        SECURITY_NAME_ABBR TEXT,
        ORG_CODE TEXT,
        REPORT_DATE TEXT,
        DATE_TYPE_CODE TEXT,
        PER_NETCASH_OPERATE REAL,
        PER_OI REAL,
        BPS REAL,
        BASIC_EPS REAL,
        DILUTED_EPS REAL,
        OPERATE_INCOME REAL,
        OPERATE_INCOME_YOY REAL,
        GROSS_PROFIT REAL,
        GROSS_PROFIT_YOY REAL,
        HOLDER_PROFIT REAL,
        HOLDER_PROFIT_YOY REAL,
        GROSS_PROFIT_RATIO REAL,
        EPS_TTM REAL,
        OPERATE_INCOME_QOQ REAL,
        NET_PROFIT_RATIO REAL,
        ROE_AVG REAL,
        GROSS_PROFIT_QOQ REAL,
        ROA REAL,
        HOLDER_PROFIT_QOQ REAL,
        ROE_YEARLY REAL,
        ROIC_YEARLY REAL,
        TAX_EBT REAL,
        OCF_SALES REAL,
        DEBT_ASSET_RATIO REAL,
        CURRENT_RATIO REAL,
        CURRENTDEBT_DEBT REAL,
        START_DATE TEXT,
        FISCAL_YEAR TEXT,
        CURRENCY TEXT,
        IS_CNY_CODE INTEGER,
        UPDATED_AT TEXT,
        PRIMARY KEY (SECURITY_CODE, REPORT_DATE, DATE_TYPE_CODE)
    )
    '''

    SQL_DELETE_BY_CODE = 'DELETE FROM hk_financial WHERE SECURITY_CODE = ?'

    SQL_INSERT_FINANCIAL = '''
    INSERT INTO hk_financial (
        SECUCODE, SECURITY_CODE, SECURITY_NAME_ABBR, ORG_CODE, REPORT_DATE, DATE_TYPE_CODE,
        PER_NETCASH_OPERATE, PER_OI, BPS, BASIC_EPS, DILUTED_EPS, OPERATE_INCOME, OPERATE_INCOME_YOY,
        GROSS_PROFIT, GROSS_PROFIT_YOY, HOLDER_PROFIT, HOLDER_PROFIT_YOY, GROSS_PROFIT_RATIO,
        EPS_TTM, OPERATE_INCOME_QOQ, NET_PROFIT_RATIO, ROE_AVG, GROSS_PROFIT_QOQ, ROA,
        HOLDER_PROFIT_QOQ, ROE_YEARLY, ROIC_YEARLY, TAX_EBT, OCF_SALES, DEBT_ASSET_RATIO,
        CURRENT_RATIO, CURRENTDEBT_DEBT, START_DATE, FISCAL_YEAR, CURRENCY, IS_CNY_CODE, UPDATED_AT
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    SQL_GET_BY_CODE_AND_DATE = 'SELECT * FROM hk_financial WHERE SECURITY_CODE = ? AND REPORT_DATE = ?'

    SQL_GET_LAST_3YEAR_REPORTS = '''
    SELECT * FROM hk_financial 
    WHERE SECURITY_CODE = ? AND DATE_TYPE_CODE = '001' 
    ORDER BY REPORT_DATE DESC 
    LIMIT 3
    '''

    SQL_GET_LAST_YEAR_REPORT = '''
    SELECT * FROM hk_financial 
    WHERE SECURITY_CODE = ? AND DATE_TYPE_CODE = '001' 
    ORDER BY REPORT_DATE DESC 
    LIMIT 1
    '''

    SQL_GET_ALL_LAST_YEAR_REPORTS = '''
    SELECT * FROM (
        SELECT * FROM hk_financial WHERE DATE_TYPE_CODE = '001' ORDER BY REPORT_DATE DESC
    ) GROUP BY SECURITY_CODE
    '''

    SQL_GET_CODE_TIME_MAP = 'SELECT SECURITY_CODE, UPDATED_AT FROM hk_financial'

    SQL_DROP_HK_FINANCIAL_TABLE = 'DROP TABLE IF EXISTS hk_financial'

    def __init__(self):
        self.db_manager = DatabaseConnectionManager()
        self.stock_service = HkStockService()
        self._init_tables()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def _init_tables(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(self.SQL_CREATE_HK_FINANCIAL_TABLE)
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_hk_financial_code ON hk_financial (SECURITY_CODE)")
        except Exception as e:
            print(f"创建索引失败: {e}")
        conn.commit()

    def _create_financial_from_row(self, row) -> HkFinancial:
        return HkFinancial(
            secucode=row[0],
            security_code=row[1],
            security_name_abbr=row[2],
            org_code=row[3],
            report_date=row[4],
            date_type_code=row[5],
            per_netcash_operate=row[6],
            per_oi=row[7],
            bps=row[8],
            basic_eps=row[9],
            diluted_eps=row[10],
            operate_income=row[11],
            operate_income_yoy=row[12],
            gross_profit=row[13],
            gross_profit_yoy=row[14],
            holder_profit=row[15],
            holder_profit_yoy=row[16],
            gross_profit_ratio=row[17],
            eps_ttm=row[18],
            operate_income_qoq=row[19],
            net_profit_ratio=row[20],
            roe_avg=row[21],
            gross_profit_qoq=row[22],
            roa=row[23],
            holder_profit_qoq=row[24],
            roe_yearly=row[25],
            roic_yearly=row[26],
            tax_ebt=row[27],
            ocf_sales=row[28],
            debt_asset_ratio=row[29],
            current_ratio=row[30],
            currentdebt_debt=row[31],
            start_date=row[32],
            fiscal_year=row[33],
            currency=row[34],
            is_cny_code=row[35],
            updated_at=row[36]
        )

    def fetch_from_api(self, code: str, indicator: str = "报告期") -> pd.DataFrame:
        try:
            df = ak.stock_financial_hk_analysis_indicator_em(symbol=code, indicator=indicator)
            return df
        except Exception as e:
            print(f"获取港股 {code} 财务数据失败: {e}")
            return pd.DataFrame()

    def get_by_code_and_date(self, security_code: str, report_date: str) -> Optional[HkFinancial]:
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute(self.SQL_GET_BY_CODE_AND_DATE, (security_code, report_date))
            row = cursor.fetchone()
            if row:
                return self._create_financial_from_row(row)
            return None
        except Exception as e:
            print(f"获取财务数据失败: {e}")
            return None

    def get_last_3year_reports(self, security_code: str) -> List[HkFinancial]:
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute(self.SQL_GET_LAST_3YEAR_REPORTS, (security_code,))
            rows = cursor.fetchall()
            return [self._create_financial_from_row(row) for row in rows]
        except Exception as e:
            print(f"获取近3年财报数据失败: {e}")
            return []

    def get_last_year_report(self, security_code: str) -> Optional[HkFinancial]:
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute(self.SQL_GET_LAST_YEAR_REPORT, (security_code,))
            row = cursor.fetchone()
            if row:
                return self._create_financial_from_row(row)
            return None
        except Exception as e:
            print(f"获取最近年报数据失败: {e}")
            return None

    def get_all_last_year_reports(self) -> List[HkFinancial]:
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute(self.SQL_GET_ALL_LAST_YEAR_REPORTS)
            rows = cursor.fetchall()
            result = []
            for row in rows:
                if row:
                    try:
                        result.append(self._create_financial_from_row(row))
                    except Exception as e:
                        print(f"创建 HkFinancial 对象失败: {e}")
                        continue
            return result
        except Exception as e:
            print(f"获取所有最近年报数据失败: {e}")
            return []

    def delete_by_code(self, security_code: str) -> bool:
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute(self.SQL_DELETE_BY_CODE, (security_code,))
            conn.commit()
            return True
        except Exception as e:
            print(f"删除财务数据失败: {e}")
            return False

    def refresh(self, security_code: str) -> bool:
        try:
            df_report = self.fetch_from_api(security_code, "报告期")
            df_year = self.fetch_from_api(security_code, "年度")
            df = pd.concat([df_report, df_year])
            df.drop_duplicates(inplace=True)

            if df.empty:
                print(f"股票 {security_code} 无财务数据")
                return False

            df['UPDATE_AT'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            self.delete_by_code(security_code)

            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            for _, row in df.iterrows():
                cursor.execute(self.SQL_INSERT_FINANCIAL, (
                    row.get('SECUCODE'),
                    row.get('SECURITY_CODE'),
                    row.get('SECURITY_NAME_ABBR'),
                    row.get('ORG_CODE'),
                    row.get('REPORT_DATE'),
                    row.get('DATE_TYPE_CODE'),
                    row.get('PER_NETCASH_OPERATE'),
                    row.get('PER_OI'),
                    row.get('BPS'),
                    row.get('BASIC_EPS'),
                    row.get('DILUTED_EPS'),
                    row.get('OPERATE_INCOME'),
                    row.get('OPERATE_INCOME_YOY'),
                    row.get('GROSS_PROFIT'),
                    row.get('GROSS_PROFIT_YOY'),
                    row.get('HOLDER_PROFIT'),
                    row.get('HOLDER_PROFIT_YOY'),
                    row.get('GROSS_PROFIT_RATIO'),
                    row.get('EPS_TTM'),
                    row.get('OPERATE_INCOME_QOQ'),
                    row.get('NET_PROFIT_RATIO'),
                    row.get('ROE_AVG'),
                    row.get('GROSS_PROFIT_QOQ'),
                    row.get('ROA'),
                    row.get('HOLDER_PROFIT_QOQ'),
                    row.get('ROE_YEARLY'),
                    row.get('ROIC_YEARLY'),
                    row.get('TAX_EBT'),
                    row.get('OCF_SALES'),
                    row.get('DEBT_ASSET_RATIO'),
                    row.get('CURRENT_RATIO'),
                    row.get('CURRENTDEBT_DEBT'),
                    row.get('START_DATE'),
                    row.get('FISCAL_YEAR'),
                    row.get('CURRENCY'),
                    row.get('IS_CNY_CODE'),
                    row.get('UPDATE_AT')
                ))

            conn.commit()

            df_yearly = df[df['DATE_TYPE_CODE'] == '001'].sort_values('REPORT_DATE', ascending=False)
            if not df_yearly.empty:
                latest_report = df_yearly.iloc[0]
                stock = Stock(
                    code=security_code,
                    market='h',
                    net_asset_per_share=latest_report.get('BPS'),
                    basic_eps=latest_report.get('BASIC_EPS'),
                    assets_debt_ratio=latest_report.get('DEBT_ASSET_RATIO'),
                    roe=latest_report.get('ROE_AVG')
                )
                self.stock_service._save_stock(stock)

            return True
        except Exception as e:
            print(f"刷新财务数据失败: {e}")
            return False

    def _get_code_time_map(self) -> Dict[str, str]:
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute(self.SQL_GET_CODE_TIME_MAP)
            rows = cursor.fetchall()
            return {row[0]: row[1] for row in rows if row[0] and row[1]}
        except Exception as e:
            print(f"获取更新时间映射失败: {e}")
            return {}

    def refresh_all(self, progress_callback: Optional[Callable[[int, int, str], None]] = None) -> int:
        time_map = self._get_code_time_map()
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        stocks = self.stock_service.get_all_stocks()

        updated_count = 0
        total = len(stocks)

        for i, stock in enumerate(stocks):
            update_at = time_map.get(stock.code)
            if update_at and update_at.startswith(today):
                continue

            if self.refresh(stock.code):
                updated_count += 1

            if progress_callback:
                progress_callback(i + 1, total, "刷新财务数据")

        print(f"港股财务数据刷新完成，共更新 {updated_count} 只股票")
        return updated_count

    def drop_tables(self):
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute(self.SQL_DROP_HK_FINANCIAL_TABLE)
            conn.commit()
            print("hk_financial 表已删除")
        except Exception as e:
            print(f"删除 hk_financial 表失败: {e}")


if __name__ == "__main__":
    service = HkFinancialService()
    service.refresh("00700")
    reports = service.get_last_3year_reports("00700")
    print(f"获取了 {len(reports)} 条财报数据")
    if reports:
        print(f"最近报告期: {reports[0].report_date}, ROE: {reports[0].roe_avg}")
