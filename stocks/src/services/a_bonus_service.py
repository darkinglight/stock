import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import akshare as ak
from typing import Optional, List
import datetime
from database.connection import DatabaseConnectionManager
from models import Bonus
from services.config_service import ConfigService
from services.a_stock_service import AStockService
from models.stock import Stock

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
        quarter TEXT,
        update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    '''
    
    SQL_DELETE_BONUS_RECORDS = "DELETE FROM bonus WHERE stock_code = ?"
    
    SQL_INSERT_BONUS_RECORDS = '''
    INSERT INTO bonus 
    (stock_code, report_period, bonus_description, bonus_amount, dividend_payout_rate, pre_tax_dividend_rate, year, quarter)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    '''
    
    SQL_GET_UPDATED_CODES = 'SELECT DISTINCT stock_code FROM bonus WHERE update_time LIKE ?'
    
    SQL_GET_ALL_BONUS_RECORDS = 'SELECT stock_code, dividend_payout_rate, year, quarter FROM bonus'
    
    def __init__(self):
        """初始化服务"""
        self.db_manager = DatabaseConnectionManager()
        self.config_service = ConfigService()
        self.stock_service = AStockService()
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
    
    def drop_bonus_table(self):
        """
        删除bonus表
        """
        try:
            self.cursor.execute("DROP TABLE IF EXISTS bonus")
            self.conn.commit()
            print("bonus表删除成功")
        except Exception as e:
            print(f"删除bonus表失败: {e}")
            try:
                self.conn.rollback()
            except:
                pass

    def _create_bonus_table(self):
        """创建分红记录表"""
        try:
            self.cursor.execute(self.SQL_CREATE_BONUS_TABLE)
            
            # 创建stock_code列的索引
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_stock_code ON bonus (stock_code)")
            
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
                    record.year,
                    record.quarter
                ))
            
            if data:
                self.cursor.executemany(self.SQL_INSERT_BONUS_RECORDS, data)
            
            self.conn.commit()
        except Exception as e:
            print(f"保存分红记录失败 (股票代码: {code}): {e}")
            try:
                self.conn.rollback()
            except:
                pass
    
    def fetch_and_save_bonus_records(self, code: str) -> int:
        """
        从API获取近3年分红数据并保存到数据库
        
        Args:
            code: A股代码
            
        Returns:
            int: 保存的记录数量
        """
        try:
            df = ak.stock_fhps_detail_ths(symbol=code)
            
            if df.empty:
                return 0
            
            current_year = datetime.datetime.now().year
            three_years_ago = current_year - 3
            
            records = []
            for _, row in df.iterrows():
                bonus = Bonus.from_row(row)
                if three_years_ago <= bonus.year <= current_year:
                    records.append(bonus)
            
            if records:
                self._save_bonus_records(code, records)
            
            return len(records)
            
        except Exception as e:
            print(f"获取并保存分红数据失败 (股票代码: {code}): {e}")
            return 0
    
    def refresh_all(self) -> int:
        self.refresh_all_bonus_records()
        return self.refresh_all_bonus_rates()
    
    def refresh_all_bonus_records(self) -> int:
        """
        全量保存所有A股的分红详细数据
        支持中断续更，跳过今天已经更新过的股票
        
        Returns:
            int: 保存的股票数量
        """
        try:
            stocks = self.stock_service._get_all_stocks()
            
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            self.cursor.execute(self.SQL_GET_UPDATED_CODES, (today + '%',))
            updated_codes = {row[0] for row in self.cursor.fetchall()}
            
            stocks_to_update = [stock for stock in stocks if stock.code not in updated_codes]
            
            total_stocks = len(stocks_to_update)
            updated_count = 0
            
            print(f"共需要保存 {total_stocks} 只股票的分红数据（已跳过 {len(updated_codes)} 只今日已更新）")
            
            for i, stock in enumerate(stocks_to_update):
                try:
                    if self.fetch_and_save_bonus_records(stock.code) > 0:
                        updated_count += 1
                except Exception as e:
                    print(f"保存股票 {stock.code} 分红数据时出错: {e}")
                
                progress = (i + 1) / total_stocks * 100
                print(f"进度: {progress:.2f}% ({i + 1}/{total_stocks})")
            
            print(f"分红数据保存完成，共保存 {updated_count} 只股票")
            return updated_count
            
        except Exception as e:
            print(f"保存分红数据失败: {e}")
            return 0
    
    def refresh_all_bonus_rates(self) -> int:
        """
        根据数据库中已保存的分红数据，全量刷新所有股票的bonus_rate
        
        Returns:
            int: 更新的股票数量
        """
        try:
            self.cursor.execute(self.SQL_GET_ALL_BONUS_RECORDS)
            all_records = self.cursor.fetchall()
            
            if not all_records:
                print("没有分红数据")
                return 0
            
            current_year = datetime.datetime.now().year
            three_years_ago = current_year - 3
            
            from collections import defaultdict
            records_by_code = defaultdict(list)
            for row in all_records:
                stock_code = row[0]
                dividend_payout_rate = row[1]
                year = row[2]
                quarter = row[3]
                if dividend_payout_rate and three_years_ago <= year <= current_year:
                    records_by_code[stock_code].append((dividend_payout_rate, quarter))
            
            total = len(records_by_code)
            updated_count = 0
            
            print(f"共需要刷新 {total} 只股票的分红率")
            
            for i, (code, records) in enumerate(records_by_code.items()):
                try:
                    rates = []
                    for dividend_payout_rate, quarter in records:
                        if quarter == 'Q1':
                            adjusted_rate = dividend_payout_rate / 4
                        elif quarter == 'Q2':
                            adjusted_rate = dividend_payout_rate / 2
                        elif quarter == 'Q3':
                            adjusted_rate = dividend_payout_rate * 3 / 4
                        else:
                            adjusted_rate = dividend_payout_rate
                        rates.append(adjusted_rate)
                    
                    if rates:
                        average_rate = sum(rates) / 3
                        average_rate = max(10.0, min(90.0, average_rate))
                        
                        stock = Stock(code=code, bonus_rate=average_rate)
                        self.stock_service._save_stock(stock)
                        updated_count += 1
                except Exception as e:
                    print(f"刷新股票 {code} 分红率时出错: {e}")
                
                progress = (i + 1) / total * 100
                print(f"进度: {progress:.2f}% ({i + 1}/{total})")
            
            print(f"分红率刷新完成，共更新 {updated_count} 只股票")
            return updated_count
            
        except Exception as e:
            print(f"刷新分红率失败: {e}")
            return 0
    
    def get_bonus_details_by_code(self, code: str) -> List[Bonus]:
        """
        根据股票代码获取分红详情列表
        
        Args:
            code: A股代码
            
        Returns:
            List[Bonus]: 分红详情列表
        """
        try:
            # 查询该股票的所有分红记录
            query = """
            SELECT stock_code, report_period, bonus_description, bonus_amount, 
                   dividend_payout_rate, pre_tax_dividend_rate, year, quarter
            FROM bonus
            WHERE stock_code = ?
            ORDER BY year DESC, quarter DESC
            """
            self.cursor.execute(query, (code,))
            rows = self.cursor.fetchall()
            
            # 转换为Bonus对象列表
            bonus_list = []
            for row in rows:
                bonus = Bonus(
                    report_period=row[1],
                    bonus_description=row[2],
                    bonus_amount=row[3],
                    dividend_payout_rate=row[4],
                    pre_tax_dividend_rate=row[5],
                    year=row[6],
                    quarter=row[7]
                )
                bonus_list.append(bonus)
            
            return bonus_list
            
        except Exception as e:
            print(f"获取分红详情失败 (股票代码: {code}): {e}")
            return []



if __name__ == "__main__":
    a_bonus_service = ABonusService()
    a_bonus_service.refresh_all_bonus_rates()
