import akshare as ak
from typing import Optional, List
import datetime
from database.connection import DatabaseConnectionManager
from models import Bonus
from services.config_service import ConfigService
from services.a_stock_service import AStockService


class ABonusService:
    """A股分红服务 - 处理A股分红率相关数据"""
    
    # SQL语句常量
    SQL_CREATE_BONUS_TABLE = '''
    CREATE TABLE IF NOT EXISTS bonus (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stock_code TEXT NOT NULL,
        report_period TEXT NOT NULL,
        bonus_description TEXT,
        bonus_amount REAL,
        dividend_payout_rate REAL,
        pre_tax_dividend_rate REAL,
        year INTEGER,
        update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_stock_code (stock_code)
    )
    '''
    
    SQL_GET_LAST_UPDATE_TIME = '''
    SELECT MAX(update_time) FROM bonus 
    WHERE stock_code = ?
    '''
    
    SQL_DELETE_BONUS_RECORDS = "DELETE FROM bonus WHERE stock_code = ?"
    
    SQL_INSERT_BONUS_RECORDS = '''
    INSERT INTO bonus 
    (stock_code, report_period, bonus_description, bonus_amount, dividend_payout_rate, pre_tax_dividend_rate, year)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    '''
    
    SQL_GET_UPDATED_CODES = 'SELECT DISTINCT stock_code FROM bonus WHERE update_time LIKE ?'
    
    def __init__(self):
        """初始化服务"""
        self.db_manager = DatabaseConnectionManager()
        self.config_service = ConfigService()
        # 初始化AStockService实例
        self.stock_service = AStockService()
        # 在初始化时获取数据库连接
        self.conn = self.db_manager.get_connection()
        self.cursor = self.conn.cursor()
        self._create_bonus_table()
    
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

    def _create_bonus_table(self):
        """创建分红记录表"""
        try:
            self.cursor.execute(self.SQL_CREATE_BONUS_TABLE)
            self.conn.commit()
        except Exception as e:
            print(f"创建表失败: {e}")
    
    def _save_bonus_records(self, code: str, records: List[Bonus]):
        """保存分红记录"""
        try:
            # 先删除旧记录
            self.cursor.execute(self.SQL_DELETE_BONUS_RECORDS, (code,))
            
            # 插入新记录
            data = []
            for record in records:
                data.append((
                    code,
                    record.report_period,
                    record.bonus_description,
                    record.bonus_amount,
                    record.dividend_payout_rate,
                    record.pre_tax_dividend_rate,
                    record.year
                ))
            
            if data:
                self.cursor.executemany(self.SQL_INSERT_BONUS_RECORDS, data)
            
            self.conn.commit()
        except Exception as e:
            print(f"保存分红记录失败: {e}")
            try:
                self.conn.rollback()
            except:
                pass
    
    def update_bonus_rate(self, code: str):
        """
        更新A股的平均分红率（基于近3年数据）
        
        Args:
            code: A股代码
            
        Returns:
            Optional[float]: 近3年的平均分红率，如果没有近3年数据返回 None
        """
        try:
            # 从同花顺获取分红配送数据
            df = ak.stock_fhps_detail_ths(symbol=code)
            
            if not df.empty:
                # 转换数据为Bonus对象列表并过滤近3年数据
                current_year = datetime.datetime.now().year
                three_years_ago = current_year - 3
                
                records = []
                for _, row in df.iterrows():
                    bonus = Bonus.from_row(row)
                    # 只保存近3年的数据
                    if bonus.year >= three_years_ago and bonus.year <= current_year:
                        records.append(bonus)
                
                # 保存记录到数据库
                self._save_bonus_records(code, records)
                
                # 直接使用records计算平均分红率
                rates = [record.dividend_payout_rate for record in records if record.dividend_payout_rate]
                
                if not rates:
                    return None
                
                # 计算近3年所有记录的平均值
                average_rate = sum(rates) / len(rates)
                
                # 更新到stock表
                self.stock_service.update_bonus_rate(code, average_rate)
                
                return average_rate
            
            return None
            
        except Exception as e:
            print(f"更新A股分红率失败: {e}")
            return None
    
    def refresh_all(self) -> int:
        """
        批量更新所有A股的分红率
        支持中断续更，跳过今天已经更新过的股票
        
        Returns:
            int: 更新的股票数量
        """
        try:
            # 获取所有A股股票
            stocks = self.stock_service._get_all_stocks()
            
            # 一次性获取所有今日已更新的股票代码
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            self.cursor.execute(self.SQL_GET_UPDATED_CODES, (today + '%',))
            updated_codes = {row[0] for row in self.cursor.fetchall()}
            
            # 过滤出需要更新的股票
            stocks_to_update = [stock for stock in stocks if stock.code not in updated_codes]
            
            total_stocks = len(stocks_to_update)
            updated_count = 0
            
            print(f"共需要更新 {total_stocks} 只股票的分红率（已跳过 {len(updated_codes)} 只今日已更新）")
            
            for i, stock in enumerate(stocks_to_update):
                try:
                    if self.update_bonus_rate(stock.code):
                        updated_count += 1
                except Exception as e:
                    print(f"更新股票 {stock.code} 分红率时出错: {e}")
                
                # 输出进度百分比
                progress = (i + 1) / total_stocks * 100
                print(f"进度: {progress:.2f}% ({i + 1}/{total_stocks})")
            
            print(f"分红率刷新完成，共更新 {updated_count} 只股票")
            return updated_count
            
        except Exception as e:
            print(f"刷新分红率失败: {e}")
            return 0



if __name__ == "__main__":
    # 测试
    a_bonus_service = ABonusService()
    
    # 测试获取平均分红率
    stock_code = "600987"
    print(f"正在测试股票代码: {stock_code}")
    average_bonus_rate = a_bonus_service.update_bonus_rate(stock_code)
    if average_bonus_rate is not None:
        print(f"A股 {stock_code} 的平均分红率: {average_bonus_rate:.2f}%")
    else:
        print(f"A股 {stock_code} 没有找到分红数据")
