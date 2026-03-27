import akshare as ak
from typing import List
from models.financial import Financial
from database.connection import DatabaseConnectionManager
import datetime
from services.a_stock_service import AStockService

class AFinancialService:
    """同花顺财务数据服务"""
    
    # SQL语句常量
    SQL_CREATE_FINANCIAL_TABLE = '''
    CREATE TABLE IF NOT EXISTS financial (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL,              -- 股票代码
        report_period TEXT NOT NULL,     -- 报告期，格式：YYYY-MM-DD
        roe REAL,                        -- 净资产收益率（当期）
        quarterly_roe REAL,              -- 季度ROE
        annualized_roe REAL,             -- 年化ROE
        net_asset_per_share REAL,        -- 每股净资产
        basic_eps REAL,                  -- 每股收益
        operating_cash_flow_per_share REAL, -- 每股经营现金流
        assets_debt_ratio REAL,          -- 资产负债率
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(code, report_period),
        INDEX idx_financial_code (code),
        INDEX idx_financial_period (report_period)
    )
    '''
    SQL_DELETE_FINANCIAL_DATA = 'DELETE FROM financial WHERE code = ?'
    SQL_INSERT_FINANCIAL_DATA = '''
    INSERT INTO financial (code, report_period, roe, quarterly_roe, net_asset_per_share, basic_eps, operating_cash_flow_per_share, assets_debt_ratio, updated_at) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    SQL_GET_UPDATED_CODES = 'SELECT DISTINCT code FROM financial WHERE updated_at LIKE ?'
    
    def __init__(self):
        """
        初始化财务服务
        """
        self.db_manager = DatabaseConnectionManager()
        # 在初始化时获取数据库连接
        self.conn = self.db_manager.get_connection()
        self.cursor = self.conn.cursor()
        self._init_tables()
        # 初始化AStockService实例
        self.stock_service = AStockService()
    
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
            if hasattr(self, 'stock_service') and self.stock_service:
                self.stock_service.close()
                self.stock_service = None
        except Exception as e:
            print(f"关闭数据库连接失败: {e}")
    
    def _init_tables(self):
        """
        初始化财务数据表
        """
        # 创建财务数据表（包含索引）
        self.cursor.execute(self.SQL_CREATE_FINANCIAL_TABLE)
        
        self.conn.commit()
    
    def get_financial_data(self, symbol: str) -> List[Financial]:
        """
        获取股票的财务数据
        
        Args:
            symbol: 股票代码
            
        Returns:
            List[Financial]: 财务数据列表
        """
        # 获取财务摘要数据
        stock_financial_abstract_new_ths_df = ak.stock_financial_abstract_new_ths(
            symbol=symbol, 
            indicator="按报告期"
        )
        
        # 按报告期分组处理数据
        financial_data = {}
        
        for _, row in stock_financial_abstract_new_ths_df.iterrows():
            report_date = row['report_date']
            metric_name = row['metric_name']
            value = row['value']
            
            # 初始化该报告期的 Financial 对象
            if report_date not in financial_data:
                financial_data[report_date] = Financial(
                    code=symbol,
                    report_period=report_date
                )
            
            # 处理不同的指标
            if metric_name == 'index_weighted_avg_roe':
                # 季度净资产收益率
                financial_data[report_date].quarterly_roe = value
            elif metric_name == 'calc_per_net_assets':
                # 每股净资产
                financial_data[report_date].net_asset_per_share = value
            elif metric_name == 'basic_eps':
                # 每股收益
                financial_data[report_date].basic_eps = value
            elif metric_name == 'index_per_operating_cash_flow_net':
                # 每股经营现金流
                financial_data[report_date].operating_cash_flow_per_share = value
            elif metric_name == 'assets_debt_ratio':
                # 资产负债率
                financial_data[report_date].assets_debt_ratio = value
        
        # 转换为列表
        financial_list = list(financial_data.values())
        
        # 按报告期降序排序
        financial_list.sort(key=lambda x: x.report_period, reverse=True)
        
        # 只保留最近12个季度的数据
        financial_list = financial_list[:12]
        
        return financial_list
    
    def save_financial_data(self, reports: List[Financial]) -> bool:
        """
        保存财务数据到数据库
        :param reports: 财务报告列表
        :return: 是否保存成功
        """
        try:
            if not reports:
                return False
            
            # 清空该股票的现有财务数据
            code = reports[0].code
            self.cursor.execute(self.SQL_DELETE_FINANCIAL_DATA, (code,))
            
            # 获取当前时间
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 保存新数据
            for report in reports:
                # 插入数据，包括roe、quarterly_roe、net_asset_per_share、basic_eps、operating_cash_flow_per_share、assets_debt_ratio，并设置updated_at
                self.cursor.execute(
                    self.SQL_INSERT_FINANCIAL_DATA,
                    (report.code, report.report_period, report.roe, report.quarterly_roe, report.net_asset_per_share, report.basic_eps, report.operating_cash_flow_per_share, report.assets_debt_ratio, current_time)
                )
            
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"保存财务数据失败: {e}")
            return False
    
    def refresh_financial_data(self) -> int:
        """
        刷新财务数据，包括ROE、季度ROE和每股净资产
        支持中断续更，剔除今天已经更新过的股票
        :return: 更新的股票数量
        """
        try:
            # 获取所有A股股票
            stocks = self.stock_service._get_all_stocks()
            
            # 一次性获取所有今日已更新的股票代码
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            
            # 查询今天更新过的股票代码，使用DISTINCT去重
            self.cursor.execute(self.SQL_GET_UPDATED_CODES, (today + '%',))
            updated_codes = {row[0] for row in self.cursor.fetchall()}
            
            # 过滤出需要更新的股票
            stocks_to_update = [stock for stock in stocks if stock.code not in updated_codes]
            
            total_stocks = len(stocks_to_update)
            updated_count = 0
            
            print(f"共需要更新 {total_stocks} 只股票的财务数据")
            
            for i, stock in enumerate(stocks_to_update):
                try:
                    if self.update_financial_data(stock.code):
                        updated_count += 1
                except Exception as e:
                    print(f"更新股票 {stock.code} 财务数据时出错: {e}")
                
                # 输出进度百分比
                progress = (i + 1) / total_stocks * 100
                print(f"进度: {progress:.2f}% ({i + 1}/{total_stocks})")
            
            print(f"财务数据刷新完成，共更新 {updated_count} 只股票")
            return updated_count
            
        except Exception as e:
            print(f"刷新财务数据失败: {e}")
            return 0
    
    def update_financial_data(self, code: str) -> bool:
        """
        更新单个股票的财务数据
        :param code: 股票代码
        :return: 是否更新成功
        """
        try:
            # 获取财务数据
            reports = self.get_financial_data(code)
            
            if not reports:
                print(f"股票 {code} 无法获取财务数据，跳过")
                return False
            
            # 保存到数据库
            success = self.save_financial_data(reports)
            
            # 更新股票的每股净资产
            self._update_stock_net_asset(code, reports)
            
            return success
        except Exception as e:
            print(f"更新股票 {code} 财务数据失败: {e}")
            return False
    
    def _update_stock_net_asset(self, code: str, reports: List[Financial]):
        """
        更新股票的每股净资产
        :param code: 股票代码
        :param reports: 财务报告列表
        """
        try:
            stock = self.stock_service._get_stock_by_code(code)
            if stock and reports:
                stock.net_asset_per_share = reports[0].net_asset_per_share
                self.stock_service._save_stock(stock)
        except Exception as e:
            print(f"更新股票 {code} 每股净资产时出错: {e}")

if __name__ == "__main__":
    # 测试
    financial_service = AFinancialService()
    financial_data = financial_service.get_financial_data("000063")
    print(financial_data)
    financial_service.save_financial_data(financial_data)