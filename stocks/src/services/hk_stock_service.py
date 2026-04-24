import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Optional, Callable
import time
from datetime import datetime
from models.stock import Stock
from database.connection import DatabaseConnectionManager
from services.config_service import ConfigService
import akshare as ak


class HkStockService:
    """港股服务 - 处理港股数据，共用stock表，通过market='h'区分"""

    SQL_SAVE_STOCK = '''
    INSERT INTO stock (code, name, market, price, pe, pb, net_asset_per_share, basic_eps, assets_debt_ratio, roe)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(code) DO UPDATE SET
        name=excluded.name,
        price=excluded.price,
        pe=excluded.pe,
        pb=excluded.pb,
        net_asset_per_share=excluded.net_asset_per_share,
        basic_eps=excluded.basic_eps,
        assets_debt_ratio=excluded.assets_debt_ratio,
        roe=excluded.roe,
        updated_at=CURRENT_TIMESTAMP
    '''

    SQL_GET_ALL_HK_STOCKS = 'SELECT code, name, market, price, pe, pb, bonus_rate, net_asset_per_share, basic_eps, assets_debt_ratio, roe, roe_stability, roe_trend, growth, created_at, updated_at FROM stock WHERE market = ?'

    SQL_GET_HK_STOCK_BY_CODE = 'SELECT code, name, market, price, pe, pb, bonus_rate, net_asset_per_share, basic_eps, assets_debt_ratio, roe, roe_stability, roe_trend, growth, created_at, updated_at FROM stock WHERE code = ? AND market = ?'

    def __init__(self):
        self.db_manager = DatabaseConnectionManager()
        self.config_service = ConfigService()
        self.refresh_config_key = "hk_stock_last_refresh"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def _create_stock_from_row(self, row):
        return Stock(
            code=row[0],
            name=row[1],
            market=row[2],
            price=row[3],
            pe=row[4],
            pb=row[5],
            bonus_rate=row[6],
            net_asset_per_share=row[7],
            basic_eps=row[8],
            assets_debt_ratio=row[9],
            roe=row[10],
            roe_stability=row[11],
            roe_trend=row[12],
            growth=row[13],
            created_at=row[14],
            updated_at=row[15]
        )

    def _should_refresh(self, key: str, interval: int) -> bool:
        last_refresh_time = self.config_service.get_last_refresh_time(key)
        current_time = time.time()

        if not last_refresh_time or (current_time - last_refresh_time) >= interval:
            return True
        return False

    def _save_stock(self, stock: Stock) -> bool:
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            existing_stock = self.get_stock_by_code(stock.code)

            if existing_stock:
                name = stock.name if stock.name is not None else existing_stock.name
                price = stock.price if stock.price is not None else existing_stock.price
                net_asset_per_share = stock.net_asset_per_share if stock.net_asset_per_share is not None else existing_stock.net_asset_per_share
                basic_eps = stock.basic_eps if stock.basic_eps is not None else existing_stock.basic_eps
                assets_debt_ratio = stock.assets_debt_ratio if stock.assets_debt_ratio is not None else existing_stock.assets_debt_ratio
                roe = stock.roe if stock.roe is not None else existing_stock.roe
            else:
                name = stock.name
                price = stock.price
                net_asset_per_share = stock.net_asset_per_share
                basic_eps = stock.basic_eps
                assets_debt_ratio = stock.assets_debt_ratio
                roe = stock.roe

            pb = None
            if price is not None and net_asset_per_share is not None and net_asset_per_share != 0:
                pb = price / net_asset_per_share

            pe = None
            if price is not None and basic_eps is not None and basic_eps != 0:
                pe = price / basic_eps

            cursor.execute(self.SQL_SAVE_STOCK, (
                stock.code, name, stock.market, price, pe, pb, net_asset_per_share, basic_eps, assets_debt_ratio, roe
            ))

            conn.commit()
            return True
        except Exception as e:
            print(f"Failed to save hk stock: {e}")
            return False



    def get_stock_by_code(self, code: str) -> Optional[Stock]:
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute(self.SQL_GET_HK_STOCK_BY_CODE, (code, 'h'))
            row = cursor.fetchone()

            if row:
                stock = self._create_stock_from_row(row)
                return stock
            return None
        except Exception as e:
            print(f"Failed to get hk stock by code: {e}")
            return None

    def get_all_stocks(self) -> List[Stock]:
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute(self.SQL_GET_ALL_HK_STOCKS, ('h',))
            rows = cursor.fetchall()

            stocks = []
            for row in rows:
                stock = self._create_stock_from_row(row)
                stocks.append(stock)

            return stocks
        except Exception as e:
            print(f"Failed to get all hk stocks: {e}")
            return []

    def get_stocks_paginated(self, page: int = 1, page_size: int = 10, sort_by: str = 'roe / pb', sort_order: str = 'desc', min_pe: Optional[float] = None, max_pe: Optional[float] = None, min_pb: Optional[float] = None, max_pb: Optional[float] = None, min_roe: Optional[float] = None, max_roe: Optional[float] = None, max_assets_debt_ratio: Optional[float] = None, min_net_asset_per_share: Optional[float] = None, min_basic_eps: Optional[float] = None) -> List[Stock]:
        try:
            if not isinstance(page, int) or page < 1:
                page = 1
            if not isinstance(page_size, int) or page_size < 1 or page_size > 100:
                page_size = 10

            offset = (page - 1) * page_size

            where_conditions = ["market = ?"]
            params = ['h']

            if min_pe is not None:
                where_conditions.append("pe >= ?")
                params.append(min_pe)
            if max_pe is not None:
                where_conditions.append("pe <= ?")
                params.append(max_pe)
            if min_pb is not None:
                where_conditions.append("pb >= ?")
                params.append(min_pb)
            if max_pb is not None:
                where_conditions.append("pb <= ?")
                params.append(max_pb)
            if min_roe is not None:
                where_conditions.append("roe >= ?")
                params.append(min_roe)
            if max_roe is not None:
                where_conditions.append("roe <= ?")
                params.append(max_roe)
            if max_assets_debt_ratio is not None:
                where_conditions.append("assets_debt_ratio <= ?")
                params.append(max_assets_debt_ratio)
            if min_net_asset_per_share is not None:
                where_conditions.append("net_asset_per_share >= ?")
                params.append(min_net_asset_per_share)
            if min_basic_eps is not None:
                where_conditions.append("basic_eps >= ?")
                params.append(min_basic_eps)

            where_clause = " WHERE " + " AND ".join(where_conditions)
            sql = f"SELECT code, name, market, price, pe, pb, bonus_rate, net_asset_per_share, basic_eps, assets_debt_ratio, roe, roe_stability, roe_trend, growth, created_at, updated_at FROM stock{where_clause} ORDER BY {sort_by} {sort_order} LIMIT ? OFFSET ?"

            params.extend([page_size, offset])

            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            stocks = []
            for row in rows:
                stock = self._create_stock_from_row(row)
                stocks.append(stock)

            return stocks
        except Exception as e:
            print(f"Failed to get hk stocks paginated: {e}")
            return []

    def refresh_stocks(self, progress_callback: Optional[Callable[[int, int, str], None]] = None) -> int:
        one_day_in_seconds = 24 * 60 * 60
        if not self._should_refresh(self.refresh_config_key, one_day_in_seconds):
            print("港股数据在1天内已更新，跳过刷新")
            return 0

        try:
            if progress_callback:
                progress_callback(0, 1, "获取数据")

            stocks = self.get_data_from_api()

            if progress_callback:
                progress_callback(1, 1, "获取数据")

            updated_count = 0
            total = len(stocks)
            for i, stock in enumerate(stocks, 1):
                if self._save_stock(stock):
                    updated_count += 1

                if progress_callback:
                    progress_callback(i, total, "保存数据")

            self.config_service.set_config(self.refresh_config_key, str(int(time.time())))
            print(f"港股数据刷新完成，共更新 {updated_count} 只股票")
            return updated_count

        except Exception as e:
            print(f"刷新港股数据失败: {e}")
            return 0

    def get_data_from_api(self) -> List[Stock]:
        stocks = []

        try:
            df = ak.stock_hk_ggt_components_em()
            df = df[["代码", "名称", "最新价"]]

            for index, row in df.iterrows():
                code = row['代码']
                name = row['名称']
                price = row['最新价']

                if price is not None and not isinstance(price, float):
                    try:
                        price = float(price)
                    except:
                        continue

                if price is not None:
                    stock = Stock(
                        code=code,
                        name=name,
                        market='h',
                        price=price
                    )
                    stocks.append(stock)

            print(f"从 API 获取了 {len(stocks)} 只港股数据")
            return stocks

        except Exception as e:
            print(f"获取港股数据失败: {e}")
            return []


if __name__ == "__main__":
    service = HkStockService()
    data = service.refresh_stocks()
    print(f"更新了 {data} 只港股")
    stocks = service.get_all_stocks()
    print(f"共有 {len(stocks)} 只港股")
    if stocks:
        print(f"第一只港股: {stocks[0].code} - {stocks[0].name}")
