from typing import List, Optional
from src.models.stock import Stock
from src.database.connection import DatabaseConnectionManager


class StockService:
    """股票服务 - 业务逻辑层"""
    
    def __init__(self):
        """
        初始化股票服务
        """
        self.db_manager = DatabaseConnectionManager()
        self._init_tables()
    
    def _init_tables(self):
        """
        初始化数据库表
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # 创建股票表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock (
            code TEXT PRIMARY KEY,           -- 股票代码
            name TEXT NOT NULL,              -- 股票名称
            market TEXT NOT NULL,            -- 市场类型 ('a' for A股, 'h' for H股)
            price REAL,                      -- 当前价格
            pe REAL,                         -- 市盈率
            pb REAL,                         -- 市净率
            bonus_rate REAL,                 -- 分红率
            market_cap REAL,                 -- 市值
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_stock_market ON stock(market)')
        
        conn.commit()
    
    def fetch_and_save_stocks(self, market: str = 'a') -> int:
        """
        从 API 获取并保存股票数据
        :param market: 市场类型
        :return: 保存的股票数量
        """
        stocks = self._fetch_from_api(market)
        count = 0
        for stock in stocks:
            if stock.validate():
                self._save_stock(stock)
                count += 1
        return count
    
    def filter_by_pe(self, min_pe: float, max_pe: float, market: str = 'a') -> List[Stock]:
        """
        根据市盈率筛选股票
        :param min_pe: 最小市盈率
        :param max_pe: 最大市盈率
        :param market: 市场类型
        :return: 筛选后的股票列表
        """
        all_stocks = self._get_all_stocks(market)
        return [s for s in all_stocks if s.pe and min_pe <= s.pe <= max_pe]
    
    def get_stock_detail(self, code: str, market: str = 'a') -> Optional[Stock]:
        """
        获取股票详情
        :param code: 股票代码
        :param market: 市场类型
        :return: 股票对象或 None
        """
        return self._get_stock_by_code(code, market)
    
    def _fetch_from_api(self, market: str) -> List[Stock]:
        """
        从外部 API 获取数据
        :param market: 市场类型
        :return: 股票列表
        """
        # 这里只是示例，实际项目中需要调用真实的 API
        # 例如使用 akshare 或 baostock
        stocks = []
        
        if market == 'a':
            # 模拟数据
            stocks = [
                Stock(code="600000", name="浦发银行", price=10.5, market="a", pe=5.2, pb=0.8, bonus_rate=0.05),
                Stock(code="600036", name="招商银行", price=35.2, market="a", pe=8.5, pb=1.2, bonus_rate=0.06),
                Stock(code="000001", name="平安银行", price=12.8, market="a", pe=4.8, pb=0.9, bonus_rate=0.04)
            ]
        elif market == 'h':
            # H股数据获取逻辑
            pass
        
        return stocks
    
    def _save_stock(self, stock: Stock) -> bool:
        """
        保存股票数据
        :param stock: 股票对象
        :return: 是否成功
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # 使用 UPSERT 语法
            cursor.execute('''
            INSERT INTO stock (code, name, market, price, pe, pb, bonus_rate, market_cap)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(code) DO UPDATE SET
                name=excluded.name,
                market=excluded.market,
                price=excluded.price,
                pe=excluded.pe,
                pb=excluded.pb,
                bonus_rate=excluded.bonus_rate,
                market_cap=excluded.market_cap,
                updated_at=CURRENT_TIMESTAMP
            ''', (
                stock.code, stock.name, stock.market, stock.price,
                stock.pe, stock.pb, stock.bonus_rate, stock.market_cap
            ))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Failed to save stock: {e}")
            return False
    
    def _get_all_stocks(self, market: str) -> List[Stock]:
        """
        获取所有股票
        :param market: 市场类型
        :return: 股票列表
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT code, name, market, price, pe, pb, bonus_rate, market_cap, created_at, updated_at FROM stock WHERE market = ?', (market,))
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
    
    def _get_stock_by_code(self, code: str, market: str) -> Optional[Stock]:
        """
        根据代码获取股票
        :param code: 股票代码
        :param market: 市场类型
        :return: 股票对象或 None
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT code, name, market, price, pe, pb, bonus_rate, market_cap, created_at, updated_at FROM stock WHERE code = ? AND market = ?', (code, market))
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
