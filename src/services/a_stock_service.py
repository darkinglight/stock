from typing import List, Optional
import time
import datetime
from models.stock import Stock
from models.financial import Financial
from database.connection import DatabaseConnectionManager
from services.a_financial_service import AFinancialService


class AStockService:
    """A股服务 - 处理A股数据"""
    
    def __init__(self):
        """
        初始化A股服务
        """
        self.db_manager = DatabaseConnectionManager()
        self._init_tables()
        self.refresh_config_key = "a_stock_last_refresh"
        self.financial_service = AFinancialService()

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
            net_asset_per_share REAL,        -- 每股净资产
            basic_eps REAL,                  -- 每股收益
            assets_debt_ratio REAL,          -- 资产负债率
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
        
        # 创建季度财务数据表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS quarterly_financial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,              -- 股票代码
            report_period TEXT NOT NULL,     -- 报告期，格式：YYYY-MM-DD
            roe REAL,                        -- 净资产收益率（当期）
            quarterly_roe REAL,              -- 季度ROE
            annualized_roe REAL,             -- 年化ROE
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(code, report_period)
        )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_quarterly_financial_code ON quarterly_financial(code)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_quarterly_financial_period ON quarterly_financial(report_period)')
        
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
            INSERT INTO stock (code, name, market, price, pe, pb, bonus_rate, net_asset_per_share, basic_eps, assets_debt_ratio)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                updated_at=CURRENT_TIMESTAMP
            ''', (
                stock.code, stock.name, stock.market, stock.price,
                stock.pe, stock.pb, stock.bonus_rate, stock.net_asset_per_share,
                stock.basic_eps, stock.assets_debt_ratio
            ))
            
            conn.commit()
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
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT code, name, market, price, pe, pb, bonus_rate, net_asset_per_share, basic_eps, assets_debt_ratio, created_at, updated_at FROM stock WHERE market IN (?, ?, ?)', ('sh', 'sz', 'bj'))
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
                    net_asset_per_share=row[7],
                    basic_eps=row[8],
                    assets_debt_ratio=row[9],
                    created_at=row[10],
                    updated_at=row[11]
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
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT code, name, market, price, pe, pb, bonus_rate, net_asset_per_share, basic_eps, assets_debt_ratio, created_at, updated_at FROM stock WHERE code = ? AND market IN (?, ?, ?)', (code, 'sh', 'sz', 'bj'))
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
                    net_asset_per_share=row[7],
                    basic_eps=row[8],
                    assets_debt_ratio=row[9],
                    created_at=row[10],
                    updated_at=row[11]
                )
                return stock
            return None
        except Exception as e:
            print(f"Failed to get stock by code: {e}")
            return None
    
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
                if stock.validate():
                    if self._save_stock(stock):
                        updated_count += 1
            
            # 更新刷新时间
            self._set_config(self.refresh_config_key, str(int(time.time())))
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
        import akshare as ak
        
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
    
    def refresh_quarterly_financial_data(self) -> int:
        """
        刷新季度财务数据，包括ROE、季度ROE和每股净资产
        支持中断续更，剔除今天已经更新过的股票
        :return: 更新的股票数量
        """
        try:
            # 获取所有A股股票
            stocks = self._get_all_stocks()
            
            # 一次性获取所有今日已更新的股票代码
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # 查询今天更新过的股票代码，使用DISTINCT去重
            cursor.execute('SELECT DISTINCT code FROM quarterly_financial WHERE updated_at LIKE ?', (today + '%',))
            updated_codes = {row[0] for row in cursor.fetchall()}
            
            # 过滤出需要更新的股票
            stocks_to_update = [stock for stock in stocks if stock.code not in updated_codes]
            
            total_stocks = len(stocks_to_update)
            updated_count = 0
            
            print(f"共需要更新 {total_stocks} 只股票的财务数据")
            
            for i, stock in enumerate(stocks_to_update):
                try:
                    if self._update_quarterly_financial_data(stock.code):
                        updated_count += 1
                except Exception as e:
                    print(f"更新股票 {stock.code} 财务数据时出错: {e}")
                
                # 输出进度百分比
                progress = (i + 1) / total_stocks * 100
                print(f"进度: {progress:.2f}% ({i + 1}/{total_stocks})")
            
            print(f"季度财务数据刷新完成，共更新 {updated_count} 只股票")
            return updated_count
            
        except Exception as e:
            print(f"刷新季度财务数据失败: {e}")
            return 0
    
    def _update_quarterly_financial_data(self, code: str) -> bool:
        """
        更新单个股票的季度财务数据
        :param code: 股票代码
        :return: 是否更新成功
        """
        try:
            # 使用FinancialThsService获取季度财务数据
            reports = self.financial_service.get_financial_data(code)
            
            if not reports:
                print(f"股票 {code} 无法获取季度财务数据，跳过")
                return False
            
            # 保存到数据库
            return self._save_quarterly_financial_data(reports)
            # 更新最新的每股净资产到stock对象
            stock = self._get_stock_by_code(code)
            if stock:
                stock.net_asset_per_share = reports[0].net_asset_per_share
                self._save_stock(stock)
            
        except Exception as e:
            print(f"更新股票 {code} 季度财务数据失败: {e}")
            return False
    
    def _save_quarterly_financial_data(self, reports: List[Financial]) -> bool:
        """
        保存季度财务数据到数据库
        :param reports: 季度财务报告列表
        :return: 是否保存成功
        """
        try:
            if not reports:
                return False
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # 清空该股票的现有季度财务数据
            code = reports[0].code
            cursor.execute('DELETE FROM quarterly_financial WHERE code = ?', (code,))
            
            # 获取当前时间
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 保存新数据
            for report in reports:
                # 插入数据，包括roe、quarterly_roe、net_asset_per_share、basic_eps、operating_cash_flow_per_share、assets_debt_ratio，并设置updated_at
                cursor.execute(
                    'INSERT INTO quarterly_financial (code, report_period, roe, quarterly_roe, net_asset_per_share, basic_eps, operating_cash_flow_per_share, assets_debt_ratio, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (report.code, report.report_period, report.roe, report.quarterly_roe, report.net_asset_per_share, report.basic_eps, report.operating_cash_flow_per_share, report.assets_debt_ratio, current_time)
                )
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"保存季度财务数据失败: {e}")
            return False
    
if __name__ == "__main__":
    service = AStockService()
    service.refresh_stocks()
    service.refresh_quarterly_financial_data()