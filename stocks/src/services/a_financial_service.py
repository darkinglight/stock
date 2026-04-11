import sys
import os
import statistics

# 添加src目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import akshare as ak
from typing import List, Optional, Callable
from models.financial import Financial
from database.connection import DatabaseConnectionManager
import datetime
from services.a_stock_service import AStockService
from models.stock import Stock

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
        net_asset_per_share REAL,        -- 每股净资产
        basic_eps REAL,                  -- 每股收益
        quarterly_eps REAL,              -- 季度每股收益
        operating_cash_flow_per_share REAL, -- 每股经营现金流
        assets_debt_ratio REAL,          -- 资产负债率
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(code, report_period)
    )
    '''
    SQL_DELETE_FINANCIAL_DATA = 'DELETE FROM financial WHERE code = ?'
    SQL_INSERT_FINANCIAL_DATA = '''
    INSERT INTO financial (code, report_period, roe, quarterly_roe, net_asset_per_share, basic_eps, quarterly_eps, operating_cash_flow_per_share, assets_debt_ratio) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    SQL_GET_UPDATED_CODES = 'SELECT DISTINCT code FROM financial WHERE updated_at LIKE ?'
    SQL_DROP_FINANCIAL_TABLE = 'DROP TABLE IF EXISTS financial'
    SQL_GET_FINANCIAL_DATA_BY_CODE = '''
    SELECT code, report_period, roe, quarterly_roe, net_asset_per_share, basic_eps, quarterly_eps, operating_cash_flow_per_share, assets_debt_ratio
    FROM financial 
    WHERE code = ? 
    ORDER BY report_period DESC
    '''
    
    def __init__(self):
        """
        初始化财务服务
        """
        self.db_manager = DatabaseConnectionManager()
        self._init_tables()
        # 初始化AStockService实例
        self.stock_service = AStockService()
    
    def drop_financial_table(self):
        """
        删除financial表
        :return: 是否删除成功
        """
        try:
            # 获取线程本地连接和游标
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(self.SQL_DROP_FINANCIAL_TABLE)
            conn.commit()
            print("financial表删除成功")
            return True
        except Exception as e:
            print(f"删除financial表失败: {e}")
            return False
    
    def _init_tables(self):
        """
        初始化财务数据表
        """
        # 获取线程本地连接和游标
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # 创建财务数据表
        cursor.execute(self.SQL_CREATE_FINANCIAL_TABLE)
        
        # 创建索引
        try:
            # 创建code列的索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_financial_code ON financial (code)")
        except Exception as e:
            print(f"创建索引失败: {e}")
        
        conn.commit()
    
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
            if metric_name not in ['index_weighted_avg_roe', 'calc_per_net_assets', 'basic_eps', 'index_per_operating_cash_flow_net', 'assets_debt_ratio']:
                continue
            # 尝试将 value 转换为浮点数
            try:
                if value is not None and value != '':
                    value = float(value)
                else:
                    value = None
            except (ValueError, TypeError):
                value = None
            
            # 初始化该报告期的 Financial 对象
            if report_date not in financial_data:
                financial_data[report_date] = Financial(
                    code=symbol,
                    report_period=report_date
                )
            
            # 处理不同的指标
            if metric_name == 'index_weighted_avg_roe':
                # 当期净资产收益率
                financial_data[report_date].roe = value
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

        # 从最近一个季度开始，获取连续的12个季度数据，如果中间不是连续的季度，则终止后续季度获取，只返回之前连续的季度数据
        consecutive_list = []
        for i, financial in enumerate(financial_list):
            # 检查 quarterly_roe 和 basic_eps 是否为空
            if financial.roe is None or financial.basic_eps is None:
                # 如果数据为空，终止
                break
                
            if i == 0:
                # 第一个元素直接添加
                consecutive_list.append(financial)
            else:
                # 获取当前和前一个报告期
                current_period = financial.report_period
                prev_period = consecutive_list[-1].report_period
                
                # 解析年和月 2025-06-30
                current_date = datetime.datetime.strptime(current_period, '%Y-%m-%d')
                prev_date = datetime.datetime.strptime(prev_period, '%Y-%m-%d')
                
                # 计算是否为连续季度
                # 连续季度的条件：两个日期之间相差3个月
                # 计算日期差（天数）
                delta = prev_date - current_date
                # 检查是否接近3个月（约90天）
                is_consecutive = abs(delta.days - 90) <= 3
                
                if is_consecutive:
                    consecutive_list.append(financial)
                else:
                    # 不连续，终止
                    break
                
                # 最多保留13个季度
                if len(consecutive_list) >= 13:
                    break
        
        # 使用连续的季度数据
        financial_list = consecutive_list
        
        # 计算quarterly_eps和quarterly_roe：根据报告期月份计算
        for i, financial in enumerate(financial_list):
            # 获取报告期月份
            month = int(financial.report_period.split('-')[1])
            
            if month == 3:
                # 3月报告期
                financial.quarterly_eps = financial.basic_eps
                financial.quarterly_roe = financial.roe
            elif month in [6, 9, 12]:
                # 6、9、12月报告期
                if i + 1 < len(financial_list):
                    prev_financial = financial_list[i + 1]
                    financial.quarterly_eps = financial.basic_eps - prev_financial.basic_eps
                    financial.quarterly_roe = financial.roe - prev_financial.roe
                else:
                    # 没有上期数据，无法计算
                    financial.quarterly_eps = None
                    financial.quarterly_roe = None
        
        # 只返回最近12个季度的数据
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
            
            # 获取线程本地连接和游标
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # 清空该股票的现有财务数据
            code = reports[0].code
            cursor.execute(self.SQL_DELETE_FINANCIAL_DATA, (code,))
            
            # 保存新数据
            for report in reports:
                # 插入数据，包括roe、quarterly_roe、net_asset_per_share、basic_eps、quarterly_eps、operating_cash_flow_per_share、assets_debt_ratio
                cursor.execute(
                    self.SQL_INSERT_FINANCIAL_DATA,
                    (report.code, report.report_period, report.roe, report.quarterly_roe, report.net_asset_per_share, report.basic_eps, report.quarterly_eps, report.operating_cash_flow_per_share, report.assets_debt_ratio)
                )
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"保存财务数据失败: {e}")
            return False
    
    def _process_single_stock(self, code):
        """
        处理单个股票的财务数据
        :param code: 股票代码
        :return: (code, reports) 或 None
        """
        try:
            # 获取财务数据
            reports = self.get_financial_data(code)
            
            if reports:
                # 保存到数据库
                if self.save_financial_data(reports):
                    return (code, reports)
            else:
                print(f"股票 {code} 无法获取财务数据，跳过")
        except Exception as e:
            print(f"保存股票 {code} 财务数据时出错: {e}")
        return None
    
    def batch_save_financial_data(self, stock_codes_to_update, progress_callback: Optional[Callable[[int, int, str], None]] = None, should_stop: Optional[Callable[[], bool]] = None):
        """
        批量保存财务数据
        :param stock_codes_to_update: 需要更新的股票代码列表
        :param progress_callback: 进度回调函数，参数为(当前进度, 总数, 阶段名称)
        :param should_stop: 停止检查回调函数，返回True表示应该停止
        :return: 成功获取财务数据的股票代码和报告列表
        """
        successful_stocks = []
        total_stocks = len(stock_codes_to_update)
        
        print(f"开始批量保存财务数据，共 {total_stocks} 只股票")
        
        for i, code in enumerate(stock_codes_to_update):
            # 检查是否应该停止
            if should_stop and should_stop():
                print("批量保存财务数据被用户中断")
                break
            
            result = self._process_single_stock(code)
            if result:
                successful_stocks.append(result)
            
            if progress_callback:
                progress_callback(i + 1, total_stocks, "获取财务数据")
        
        print(f"财务数据保存完成，共成功保存 {len(successful_stocks)} 只股票")
        return successful_stocks
    
    def batch_update_stock_data(self, successful_stocks, progress_callback: Optional[Callable[[int, int, str], None]] = None, should_stop: Optional[Callable[[], bool]] = None):
        """
        批量更新股票数据
        :param successful_stocks: 成功获取财务数据的股票代码和报告列表
        :param progress_callback: 进度回调函数，参数为(当前进度, 总数, 阶段名称)
        :param should_stop: 停止检查回调函数，返回True表示应该停止
        :return: 更新成功的股票数量
        """
        updated_count = 0
        total_stocks = len(successful_stocks)
        
        print(f"开始批量更新股票数据，共 {total_stocks} 只股票")
        
        for i, (code, reports) in enumerate(successful_stocks):
            # 检查是否应该停止
            if should_stop and should_stop():
                print("批量更新股票数据被用户中断")
                break
            
            try:
                self._update_stock_data(code, reports)
                updated_count += 1
            except Exception as e:
                print(f"更新股票 {code} 数据时出错: {e}")
            
            if progress_callback:
                progress_callback(i + 1, total_stocks, "更新股票数据")
        
        return updated_count
    
    def refresh_financial_data(self, progress_callback: Optional[Callable[[int, int, str], None]] = None, should_stop: Optional[Callable[[], bool]] = None) -> int:
        """
        刷新财务数据，包括ROE、季度ROE和每股净资产
        支持中断续更，剔除今天已经更新过的股票
        :param progress_callback: 进度回调函数，参数为(当前进度, 总数, 阶段名称)
        :param should_stop: 停止检查回调函数，返回True表示应该停止
        :return: 更新的股票数量
        """
        try:
            stocks = self.stock_service._get_all_stocks()
            
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            
            # 获取线程本地连接和游标
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(self.SQL_GET_UPDATED_CODES, (today + '%',))
            updated_codes = {row[0] for row in cursor.fetchall()}
            
            stock_codes_to_update = [stock.code for stock in stocks if stock.code not in updated_codes]
            
            total_stocks = len(stock_codes_to_update)
            
            print(f"共需要更新 {total_stocks} 只股票的财务数据")
            
            successful_stocks = self.batch_save_financial_data(stock_codes_to_update, progress_callback, should_stop)
            
            # 检查是否应该停止
            if should_stop and should_stop():
                print("财务数据刷新被用户中断")
                return 0
            
            updated_count = self.batch_update_stock_data(successful_stocks, progress_callback, should_stop)
            
            print(f"财务数据刷新完成，共更新 {updated_count} 只股票")
            return updated_count
            
        except Exception as e:
            print(f"刷新财务数据失败: {e}")
            return 0
    
    def update_stock_data_from_db(self) -> int:
        """
        根据数据库中的财报数据更新stock数据
        :return: 更新成功的股票数量
        """
        try:
            # 获取所有A股股票
            stocks = self.stock_service._get_all_stocks()
            
            updated_count = 0
            total_stocks = len(stocks)
            
            print(f"开始根据数据库财报数据更新股票数据，共 {total_stocks} 只股票")
            
            for i, stock in enumerate(stocks):
                try:
                    # 调用抽取的方法更新单个股票数据
                    if self._update_single_stock_from_db(stock.code):
                        updated_count += 1
                        
                except Exception as e:
                    print(f"更新股票 {stock.code} 数据时出错: {e}")
                
                # 输出进度百分比
                progress = (i + 1) / total_stocks * 100
                print(f"进度: {progress:.2f}% ({i + 1}/{total_stocks})")
            
            print(f"股票数据更新完成，共更新 {updated_count} 只股票")
            return updated_count
            
        except Exception as e:
            print(f"更新股票数据失败: {e}")
            return 0
    
    def _update_single_stock_from_db(self, code: str) -> bool:
        """
        根据数据库中的财报数据更新单个股票数据
        :param code: 股票代码
        :return: 是否更新成功
        """
        try:
            # 获取线程本地连接和游标
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # 从数据库获取该股票的财报数据
            cursor.execute(self.SQL_GET_FINANCIAL_DATA_BY_CODE, (code,))
            rows = cursor.fetchall()
            
            if not rows:
                return False
            
            # 将数据库记录转换为Financial对象列表
            reports = []
            for row in rows:
                financial = Financial(
                    code=row[0],
                    report_period=row[1],
                    roe=row[2],
                    quarterly_roe=row[3],
                    net_asset_per_share=row[4],
                    basic_eps=row[5],
                    quarterly_eps=row[6],
                    operating_cash_flow_per_share=row[7],
                    assets_debt_ratio=row[8]
                )
                reports.append(financial)
            
            # 更新股票数据
            self._update_stock_data(code, reports)
            return True
            
        except Exception as e:
            print(f"更新股票 {code} 数据时出错: {e}")
            return False
    
    def _update_stock_data(self, code: str, reports: List[Financial]):
        """
        更新股票数据
        1. roe = sum(季度roe) / length * 4
        2. 每股净资产
        3. 每股收益 = 近4季度每股收益和 
        4. 资产负债率
        5. ROE稳定性得分
        :param code: 股票代码
        :param reports: 财务报告列表
        """
        try:
            if reports:
                # 计算ROE = sum(quarterly_roe) / length * 4
                quarterly_roes = [r.quarterly_roe for r in reports if r.quarterly_roe]
                avg_roe = None
                roe_stability = None
                roe_trend = None
                if quarterly_roes:
                    avg_roe = sum(quarterly_roes) / len(quarterly_roes) * 4
                    
                    # 计算ROE稳定性得分（比较连续4个季度之间的波动）
                    if len(quarterly_roes) >= 8:  # 需要至少8个季度数据才能形成连续的4季度组合
                        # 计算连续4个季度的组合（滑动窗口）
                        four_quarter_combos = []
                        for i in range(len(quarterly_roes) - 3):
                            combo = quarterly_roes[i:i+4]
                            # 计算每个4季度组合的平均值
                            combo_avg = sum(combo) / 4
                            four_quarter_combos.append(combo_avg)
                        
                        # 计算这些4季度组合之间的差异（标准差）
                        if len(four_quarter_combos) >= 2:
                            # 计算组合间的标准差（越小越稳定）
                            combo_std = statistics.stdev(four_quarter_combos)
                            
                            # 计算组合间的趋势（斜率）
                            # 由于数据是按时间倒序排列的（最近的在前），需要反转x值
                            # 或者反转数据列表，使时间顺序为从远到近
                            x = list(range(len(four_quarter_combos)))
                            # 反转x值，使得最近的数据对应最大的x值
                            x = [len(four_quarter_combos) - 1 - i for i in x]
                            n = len(x)
                            sum_x = sum(x)
                            sum_y = sum(four_quarter_combos)
                            sum_xy = sum(x[i] * four_quarter_combos[i] for i in range(n))
                            sum_x2 = sum(x[i] ** 2 for i in range(n))
                            
                            # 计算斜率
                            if n * sum_x2 - sum_x ** 2 != 0:
                                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
                            else:
                                slope = 0
                            
                            # 计算稳定性得分（0-100）
                            # 标准差标准化（假设标准差不超过2）
                            roe_stability = min(100, max(0, (1 - combo_std / 2) * 100))
                            # 计算趋势得分（-100到100），正斜率为正分，负斜率为负分
                            roe_trend = min(100, max(-100, slope * 300))
                
                # 计算EPS，逻辑同ROE
                quarterly_eps_list = [r.quarterly_eps for r in reports if r.quarterly_eps]
                annualized_eps = None
                if quarterly_eps_list:
                    annualized_eps = sum(quarterly_eps_list) / len(quarterly_eps_list) * 4
                
                # 直接构造Stock对象
                stock = Stock(
                    code=code,
                    roe=avg_roe,
                    roe_stability=roe_stability,
                    roe_trend=roe_trend,
                    net_asset_per_share=reports[0].net_asset_per_share,
                    basic_eps=annualized_eps,
                    assets_debt_ratio=reports[0].assets_debt_ratio
                )
                
                # 保存更新
                self.stock_service._save_stock(stock)
        except Exception as e:
            print(f"更新股票 {code} 数据时出错: {e}")
    
    def get_financial_reports_by_code(self, code: str) -> List[Financial]:
        """
        根据股票代码查询财报列表
        
        Args:
            code: 股票代码
            
        Returns:
            List[Financial]: 财报数据列表
        """
        try:
            # 获取线程本地连接和游标
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # 从数据库获取该股票的财报数据
            cursor.execute(self.SQL_GET_FINANCIAL_DATA_BY_CODE, (code,))
            rows = cursor.fetchall()
            
            # 将数据库记录转换为Financial对象列表
            reports = []
            for row in rows:
                financial = Financial(
                    code=row[0],
                    report_period=row[1],
                    roe=row[2],
                    quarterly_roe=row[3],
                    net_asset_per_share=row[4],
                    basic_eps=row[5],
                    quarterly_eps=row[6],
                    operating_cash_flow_per_share=row[7],
                    assets_debt_ratio=row[8]
                )
                reports.append(financial)
            
            return reports
            
        except Exception as e:
            print(f"获取财报数据失败 (股票代码: {code}): {e}")
            return []

if __name__ == "__main__":
    # 测试
    financial_service = AFinancialService()
    # 测试删除financial表
    # financial_service.drop_financial_table()
    # 测试刷新财务数据（会重新创建表）
    # financial_service.refresh_financial_data()
    financial_service._process_single_stock("301057")
   