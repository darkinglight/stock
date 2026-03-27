from typing import List, Optional
import time
from models.stock import Stock
from database.connection import DatabaseConnectionManager
from services.config_service import ConfigService
import akshare as ak


class AStockService:
    """A股服务 - 处理A股数据"""
    
    # SQL语句常量
    SQL_CREATE_STOCK_TABLE = '''
    CREATE TABLE IF NOT EXISTS stock (
        code TEXT PRIMARY KEY,           -- 股票代码
        name TEXT NOT NULL,              -- 股票名称
        market TEXT NOT NULL,            -- 市场类型 ('sh' for 沪市, 'sz' for 深市, 'bj' for 京市, 'h' for H股)
        price REAL,                      -- 当前价格
        pe REAL,                         -- 市盈率
        pb REAL,                         -- 市净率
        bonus_rate REAL,                 -- 分红率
        net_asset_per_share REAL,        -- 每股净资产
        basic_eps REAL,                  -- 每股收益
        assets_debt_ratio REAL,          -- 资产负债率
        roe REAL,                        -- 净资产收益率
        growth REAL,                     -- 内在增长率
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_stock_market (market)
    )
    '''
    
    SQL_SAVE_STOCK = '''
    INSERT INTO stock (code, name, market, price, pe, pb, bonus_rate, net_asset_per_share, basic_eps, assets_debt_ratio, roe, growth)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(code) DO UPDATE SET
        name=excluded.name,
        market=excluded.market,
        price=excluded.price,
        pe=excluded.pe,
        pb=excluded.pb,
        bonus_rate=excluded.bonus_rate,
        net_asset_per_share=excluded.net_asset_per_share,
        basic_eps=excluded.basic_eps,
        assets_debt_ratio=excluded.assets_debt_ratio,
        roe=excluded.roe,
        growth=excluded.growth,
        updated_at=CURRENT_TIMESTAMP
    '''
    
    SQL_GET_ALL_STOCKS = 'SELECT code, name, market, price, pe, pb, bonus_rate, net_asset_per_share, basic_eps, assets_debt_ratio, roe, growth, created_at, updated_at FROM stock WHERE market IN (?, ?, ?)'
    
    SQL_GET_STOCK_BY_CODE = 'SELECT code, name, market, price, pe, pb, bonus_rate, net_asset_per_share, basic_eps, assets_debt_ratio, roe, growth, created_at, updated_at FROM stock WHERE code = ? AND market IN (?, ?, ?)'
    
    SQL_GET_STOCKS_PAGINATED = 'SELECT code, name, market, price, pe, pb, bonus_rate, net_asset_per_share, basic_eps, assets_debt_ratio, roe, growth, created_at, updated_at FROM stock WHERE market IN (?, ?, ?) ORDER BY {order_by} {order_dir} LIMIT ? OFFSET ?'
    
    SQL_GET_STOCKS_COUNT = 'SELECT COUNT(*) FROM stock WHERE market IN (?, ?, ?)'
    
    def __init__(self):
        """
        初始化A股服务
        """
        self.db_manager = DatabaseConnectionManager()
        self.config_service = ConfigService()
        # 在初始化时获取数据库连接
        self.conn = self.db_manager.get_connection()
        self.cursor = self.conn.cursor()
        self._init_tables()
        self.refresh_config_key = "a_stock_last_refresh"
    
    def __enter__(self):
        """
        上下文管理器入口
        :return: 当前实例
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        上下文管理器出口，关闭连接
        :param exc_type: 异常类型
        :param exc_val: 异常值
        :param exc_tb: 异常追踪
        """
        self.close()
    
    def close(self):
        """
        关闭数据库连接
        """
        try:
            if hasattr(self, 'cursor') and self.cursor:
                self.cursor.close()
                self.cursor = None
            if hasattr(self, 'conn') and self.conn:
                self.conn.close()
                self.conn = None
        except Exception as e:
            print(f"关闭数据库连接失败: {e}")

    def _init_tables(self):
        """
        初始化数据库表
        """
        # 创建股票表（包含索引）
        self.cursor.execute(self.SQL_CREATE_STOCK_TABLE)
        
        self.conn.commit()
    
    def _should_refresh(self, key: str, interval: int) -> bool:
        """
        检查是否需要刷新
        :param key: 配置键
        :param interval: 刷新间隔（秒）
        :return: 是否需要刷新
        """
        last_refresh_time = self.config_service.get_last_refresh_time(key)
        current_time = time.time()
        
        # 如果没有刷新过或间隔超过指定时间，则需要刷新
        if not last_refresh_time or (current_time - last_refresh_time) >= interval:
            return True
        return False
    
    def _save_stock(self, stock: Stock) -> bool:
        """
        保存股票数据
        :param stock: 股票对象
        :return: 是否成功
        """
        try:
            # 查询数据库中已有的记录
            existing_stock = self._get_stock_by_code(stock.code)
            
            if existing_stock:
                # 先更新基础字段，如果有值则更新到已有记录上
                if stock.name:
                    existing_stock.name = stock.name
                if stock.market:
                    existing_stock.market = stock.market
                if stock.price:
                    existing_stock.price = stock.price
                if stock.net_asset_per_share:
                    existing_stock.net_asset_per_share = stock.net_asset_per_share
                if stock.basic_eps:
                    existing_stock.basic_eps = stock.basic_eps
                if stock.bonus_rate:
                    existing_stock.bonus_rate = stock.bonus_rate
                if stock.assets_debt_ratio:
                    existing_stock.assets_debt_ratio = stock.assets_debt_ratio
                if stock.roe:
                    existing_stock.roe = stock.roe
            else:
                # 如果不存在该 stock 记录，直接使用新 stock
                existing_stock = stock
            
            # 再更新需要计算的字段
            if existing_stock.net_asset_per_share and existing_stock.net_asset_per_share > 0:
                existing_stock.pb = existing_stock.price / existing_stock.net_asset_per_share
            if existing_stock.basic_eps and existing_stock.basic_eps > 0:
                existing_stock.pe = existing_stock.price / existing_stock.basic_eps
            # 计算内在增长率
            if (existing_stock.roe and existing_stock.roe > 0 and 
                existing_stock.bonus_rate is not None and 
                existing_stock.pb and existing_stock.pb > 0):
                existing_stock.growth = existing_stock.roe * (1 - existing_stock.bonus_rate) + existing_stock.roe * existing_stock.bonus_rate / existing_stock.pb
            
            # 使用 UPSERT 语法
            self.cursor.execute(self.SQL_SAVE_STOCK, (
                existing_stock.code, existing_stock.name, existing_stock.market, existing_stock.price,
                existing_stock.pe, existing_stock.pb, existing_stock.bonus_rate, existing_stock.net_asset_per_share,
                existing_stock.basic_eps, existing_stock.assets_debt_ratio, existing_stock.roe, existing_stock.growth
            ))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Failed to save stock: {e}")
            return False

    def _get_all_stocks(self) -> List[Stock]:
        """
        获取所有A股
        :return: 股票列表
        """
        try:
            self.cursor.execute(self.SQL_GET_ALL_STOCKS, ('sh', 'sz', 'bj'))
            rows = self.cursor.fetchall()
            
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
                    net_asset_per_share=row[7],
                    basic_eps=row[8],
                    assets_debt_ratio=row[9],
                    roe=row[10],
                    growth=row[11],
                    created_at=row[12],
                    updated_at=row[13]
                )
                stocks.append(stock)
            
            return stocks
        except Exception as e:
            print(f"Failed to get all stocks: {e}")
            return []
    
    def _get_stock_by_code(self, code: str) -> Optional[Stock]:
        """
        根据代码获取A股
        :param code: 股票代码
        :return: 股票对象或 None
        """
        try:
            self.cursor.execute(self.SQL_GET_STOCK_BY_CODE, (code, 'sh', 'sz', 'bj'))
            row = self.cursor.fetchone()
            
            if row:
                stock = Stock(
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
                    growth=row[11],
                    created_at=row[12],
                    updated_at=row[13]
                )
                return stock
            return None
        except Exception as e:
            print(f"Failed to get stock by code: {e}")
            return None
    
    def get_stocks_paginated(self, page: int = 1, page_size: int = 10, sort_by: str = 'growth', sort_order: str = 'desc') -> dict:
        """
        分页查询A股股票列表，支持按 growth 或 pe 排序
        :param page: 页码，默认1
        :param page_size: 每页数量，默认10
        :param sort_by: 排序字段，支持 'growth' 或 'pe'，默认 'growth'
        :param sort_order: 排序顺序，支持 'asc' 或 'desc'，默认 'desc'
        :return: 包含股票列表和总记录数的字典
        """
        try:
            # 验证页码和每页数量
            if not isinstance(page, int) or page < 1:
                page = 1
            if not isinstance(page_size, int) or page_size < 1 or page_size > 100:
                page_size = 10
            
            # 验证排序字段（防止SQL注入）
            valid_sort_fields = ['growth', 'pe']
            if sort_by not in valid_sort_fields:
                sort_by = 'growth'
            
            # 验证排序顺序（防止SQL注入）
            valid_sort_orders = ['asc', 'desc']
            if sort_order not in valid_sort_orders:
                sort_order = 'desc'
            
            # 计算偏移量
            offset = (page - 1) * page_size
            
            # 构建排序SQL
            order_by_sql = self.SQL_GET_STOCKS_PAGINATED.format(order_by=sort_by, order_dir=sort_order)
            
            # 查询分页数据
            self.cursor.execute(order_by_sql, ('sh', 'sz', 'bj', page_size, offset))
            rows = self.cursor.fetchall()
            
            # 构建股票列表
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
                    net_asset_per_share=row[7],
                    basic_eps=row[8],
                    assets_debt_ratio=row[9],
                    roe=row[10],
                    growth=row[11],
                    created_at=row[12],
                    updated_at=row[13]
                )
                stocks.append(stock)
            
            # 查询总记录数
            self.cursor.execute(self.SQL_GET_STOCKS_COUNT, ('sh', 'sz', 'bj'))
            total_count = self.cursor.fetchone()[0]
            
            # 计算总页数
            total_pages = (total_count + page_size - 1) // page_size
            
            # 返回结果
            return {
                'stocks': stocks,
                'total_count': total_count,
                'total_pages': total_pages,
                'current_page': page,
                'page_size': page_size,
                'sort_by': sort_by,
                'sort_order': sort_order
            }
        except Exception as e:
            print(f"Failed to get stocks paginated: {e}")
            return {
                'stocks': [],
                'total_count': 0,
                'total_pages': 0,
                'current_page': page,
                'page_size': page_size,
                'sort_by': sort_by,
                'sort_order': sort_order
            }
    
    def refresh_stocks(self) -> int:
        """
        刷新A股股票数据（代码、名称、最新价）
        1天内不重复更新
        :return: 更新的股票数量
        """
        # 检查是否需要刷新（1天间隔）
        one_day_in_seconds = 24 * 60 * 60
        if not self._should_refresh(self.refresh_config_key, one_day_in_seconds):
            print("A股数据在1天内已更新，跳过刷新")
            return 0
        
        try:
            # 从API获取全量股票数据
            stocks = self._refresh_from_api()
            
            updated_count = 0
            for stock in stocks:
                if self._save_stock(stock):
                    updated_count += 1
            
            # 更新刷新时间
            self.config_service.set_config(self.refresh_config_key, str(int(time.time())))
            print(f"A股数据刷新完成，共更新 {updated_count} 只股票")
            return updated_count
            
        except Exception as e:
            print(f"刷新A股数据失败: {e}")
            return 0
    
    def _refresh_from_api(self) -> List[Stock]:
        """
        从外部 API 获取全量A股数据（股票代码、名称、最新价）
        使用 akshare 的 stock_zh_a_spot 功能
        :return: 股票列表
        """
        stocks = []
        
        try:
            # 从 akshare 获取全量A股数据
            stock_zh_a_spot_df = ak.stock_zh_a_spot()
            
            # 处理查询结果
            for index, row in stock_zh_a_spot_df.iterrows():
                code = row['代码']  # 股票代码，格式如 sh600000
                name = row['名称']  # 股票名称
                price = row['最新价']  # 最新价
                
                # 提取市场代码
                if code.startswith('sh'):
                    market = 'sh'
                    stock_code = code[2:]  # 去掉 sh 前缀
                elif code.startswith('sz'):
                    market = 'sz'
                    stock_code = code[2:]  # 去掉 sz 前缀
                elif code.startswith('bj'):
                    market = 'bj'
                    stock_code = code[2:]  # 去掉 bj 前缀
                else:
                    continue  # 跳过非A股
                
                if price is not None and not isinstance(price, float):
                    try:
                        price = float(price)
                    except:
                        continue
                
                if price is not None:
                    # 创建股票对象
                    stock = Stock(
                        code=stock_code,
                        name=name,
                        market=market,
                        price=price
                    )
                    stocks.append(stock)
            
            print(f"从 akshare API 获取了 {len(stocks)} 只A股数据")
            return stocks
            
        except Exception as e:
            print(f"获取A股数据失败: {e}")
            return []
    
if __name__ == "__main__":
    service = AStockService()
    # 刷新股票数据
    service.refresh_stocks()
    
    # 测试分页查询 - 按 growth 降序
    print("\n测试分页查询 - 按 growth 降序:")
    result_growth = service.get_stocks_paginated(page=1, page_size=10, sort_by='growth', sort_order='desc')
    print(f"总记录数: {result_growth['total_count']}")
    print(f"总页数: {result_growth['total_pages']}")
    print(f"当前页: {result_growth['current_page']}")
    print("前10只股票（按 growth 降序）:")
    for i, stock in enumerate(result_growth['stocks'], 1):
        print(f"{i}. {stock.code} - {stock.name} - growth: {stock.growth:.4f}")
    
    # 测试分页查询 - 按 pe 升序
    print("\n测试分页查询 - 按 pe 升序:")
    result_pe = service.get_stocks_paginated(page=1, page_size=10, sort_by='pe', sort_order='asc')
    print(f"总记录数: {result_pe['total_count']}")
    print(f"总页数: {result_pe['total_pages']}")
    print(f"当前页: {result_pe['current_page']}")
    print("前10只股票（按 pe 升序）:")
    for i, stock in enumerate(result_pe['stocks'], 1):
        print(f"{i}. {stock.code} - {stock.name} - pe: {stock.pe:.4f}")
    
    # 关闭连接
    service.close()