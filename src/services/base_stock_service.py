from typing import List, Optional
import time
from src.models.stock import Stock
from src.database.connection import DatabaseConnectionManager


class BaseStockService:
    """基础股票服务 - 业务逻辑层"""
    
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
            market TEXT NOT NULL,            -- 市场类型 ('sh' for 沪市, 'sz' for 深市, 'bj' for 京市, 'h' for H股)
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
        
        # 创建配置表，用于记录刷新时间
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,            -- 配置键
            value TEXT NOT NULL,             -- 配置值
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
    
    def _set_config(self, key: str, value: str):
        """
        设置配置
        :param key: 配置键
        :param value: 配置值
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO config (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value=excluded.value,
                updated_at=CURRENT_TIMESTAMP
            ''', (key, value))
            
            conn.commit()
        except Exception as e:
            print(f"设置配置失败: {e}")
    
    def _get_config(self, key: str) -> Optional[str]:
        """
        获取配置
        :param key: 配置键
        :return: 配置值，不存在返回None
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT value FROM config WHERE key = ?', (key,))
            result = cursor.fetchone()
            
            if result and result[0]:
                return result[0]
            return None
        except Exception as e:
            print(f"获取配置失败: {e}")
            return None
    
    def _get_last_refresh_time(self, key: str) -> Optional[float]:
        """
        获取上次刷新时间
        :param key: 配置键
        :return: 上次刷新时间的时间戳，None表示未刷新过
        """
        try:
            value = self._get_config(key)
            if value:
                return float(value)
            return None
        except Exception as e:
            print(f"获取上次刷新时间失败: {e}")
            return None
    
    def _should_refresh(self, key: str, interval: int) -> bool:
        """
        检查是否需要刷新
        :param key: 配置键
        :param interval: 刷新间隔（秒）
        :return: 是否需要刷新
        """
        last_refresh_time = self._get_last_refresh_time(key)
        current_time = time.time()
        
        # 如果没有刷新过或间隔超过指定时间，则需要刷新
        if not last_refresh_time or (current_time - last_refresh_time) >= interval:
            return True
        return False
    
    def fetch_and_save_stocks(self) -> int:
        """
        从 API 获取并保存股票数据
        :return: 保存的股票数量
        """
        stocks = self._fetch_from_api()
        count = 0
        for stock in stocks:
            if stock.validate():
                self._save_stock(stock)
                count += 1
        return count
    
    def filter_by_pe(self, min_pe: float, max_pe: float) -> List[Stock]:
        """
        根据市盈率筛选股票
        :param min_pe: 最小市盈率
        :param max_pe: 最大市盈率
        :return: 筛选后的股票列表
        """
        all_stocks = self._get_all_stocks()
        return [s for s in all_stocks if s.pe and min_pe <= s.pe <= max_pe]
    
    def get_stock_detail(self, code: str) -> Optional[Stock]:
        """
        获取股票详情
        :param code: 股票代码
        :return: 股票对象或 None
        """
        return self._get_stock_by_code(code)
    
    def _refresh_from_api(self) -> List[Stock]:
        """
        从外部 API 获取数据
        :return: 股票列表
        """
        raise NotImplementedError("子类必须实现此方法")
    
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
    
    def _get_all_stocks(self) -> List[Stock]:
        """
        获取所有股票
        :return: 股票列表
        """
        raise NotImplementedError("子类必须实现此方法")
    
    def _get_stock_by_code(self, code: str) -> Optional[Stock]:
        """
        根据代码获取股票
        :param code: 股票代码
        :return: 股票对象或 None
        """
        raise NotImplementedError("子类必须实现此方法")
