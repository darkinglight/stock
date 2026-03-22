from typing import List, Optional
from models.stock import Stock
from services.base_stock_service import BaseStockService


class HStockService(BaseStockService):
    """H股服务 - 处理H股数据"""
    
    def _fetch_from_api(self) -> List[Stock]:
        """
        从外部 API 获取H股数据
        :return: 股票列表
        """
        import akshare as ak
        stocks = []
        
        # 使用 akshare 获取 H 股数据
        try:
            df = ak.stock_hk_spot()
            # 只获取前50条数据作为示例
            for _, row in df.head(50).iterrows():
                code = row['代码']
                name = row['名称']
                price = row['最新价']
                
                # 创建 Stock 对象
                stock = Stock(
                    code=code,
                    name=name,
                    price=price,
                    market="h"
                )
                stocks.append(stock)
        except Exception as e:
            print(f"获取 H 股数据失败: {e}")
        
        return stocks
    
    def _get_all_stocks(self) -> List[Stock]:
        """
        获取所有H股
        :return: 股票列表
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT code, name, market, price, pe, pb, bonus_rate, market_cap, created_at, updated_at FROM stock WHERE market = ?', ('h',))
            rows = cursor.fetchall()
            
            stocks = []
            for row in rows:
                stock = Stock(
                    code=row[0],
                    name=row[1],
                    market=row[2],
                    price=row[3],
                    pe=row[4],
                    pb=row[5],
                    bonus_rate=row[6],
                    market_cap=row[7],
                    created_at=row[8],
                    updated_at=row[9]
                )
                stocks.append(stock)
            
            return stocks
        except Exception as e:
            print(f"Failed to get all stocks: {e}")
            return []
    
    def _get_stock_by_code(self, code: str) -> Optional[Stock]:
        """
        根据代码获取H股
        :param code: 股票代码
        :return: 股票对象或 None
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT code, name, market, price, pe, pb, bonus_rate, market_cap, created_at, updated_at FROM stock WHERE code = ? AND market = ?', (code, 'h'))
            row = cursor.fetchone()
            
            if row:
                stock = Stock(
                    code=row[0],
                    name=row[1],
                    market=row[2],
                    price=row[3],
                    pe=row[4],
                    pb=row[5],
                    bonus_rate=row[6],
                    market_cap=row[7],
                    created_at=row[8],
                    updated_at=row[9]
                )
                return stock
            return None
        except Exception as e:
            print(f"Failed to get stock by code: {e}")
            return None
