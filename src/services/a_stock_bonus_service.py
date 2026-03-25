import akshare as ak
from typing import Optional, List
import datetime
from database.connection import DatabaseConnectionManager
from models import Bonus


class AStockBonusService:
    """A股分红服务 - 处理A股分红率相关数据"""
    
    def __init__(self):
        """初始化服务"""
        self.db_manager = DatabaseConnectionManager()
        self._create_bonus_table()
    
    def _create_bonus_table(self):
        """创建分红记录表"""
        sql = """
        CREATE TABLE IF NOT EXISTS a_stock_bonus (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_code TEXT NOT NULL,
            report_period TEXT NOT NULL,
            bonus_description TEXT,
            bonus_amount REAL,
            dividend_payout_rate REAL,
            pre_tax_dividend_rate REAL,
            year INTEGER,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
        except Exception as e:
            print(f"创建表失败: {e}")
    
    def _get_last_update_time(self, code: str) -> Optional[datetime.datetime]:
        """获取上次更新时间"""
        sql = """
        SELECT MAX(update_time) FROM a_stock_bonus 
        WHERE stock_code = ?
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute(sql, (code,))
            result = cursor.fetchone()
            if result and result[0]:
                return datetime.datetime.fromisoformat(result[0])
        except Exception as e:
            print(f"获取上次更新时间失败: {e}")
        return None
    
    def _should_update(self, code: str) -> bool:
        """检查是否需要更新数据（上次更新时间超过1周）"""
        last_update = self._get_last_update_time(code)
        if not last_update:
            return True
        
        days_since_update = (datetime.datetime.now() - last_update).days
        return days_since_update >= 7
    
    def _save_bonus_records(self, code: str, records: List[Bonus]):
        """保存分红记录"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # 先删除旧记录
            delete_sql = "DELETE FROM a_stock_bonus WHERE stock_code = ?"
            cursor.execute(delete_sql, (code,))
            
            # 插入新记录
            insert_sql = """
            INSERT INTO a_stock_bonus 
            (stock_code, report_period, bonus_description, bonus_amount, dividend_payout_rate, pre_tax_dividend_rate, year)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
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
                cursor.executemany(insert_sql, data)
            
            conn.commit()
        except Exception as e:
            print(f"保存分红记录失败: {e}")
            try:
                conn.rollback()
            except:
                pass
    
    def get_bonus_rate(self, code: str) -> Optional[float]:
        """
        获取A股的平均分红率（基于近3年数据）
        
        Args:
            code: A股代码
            
        Returns:
            Optional[float]: 近3年的平均分红率，如果没有近3年数据返回 None
        """
        try:
            # 检查是否需要更新数据
            if self._should_update(code):
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
            
            # 从数据库获取所有数据（已过滤）
            sql = """
            SELECT dividend_payout_rate FROM a_stock_bonus 
            WHERE stock_code = ?
            """
            
            rates = []
            try:
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                
                cursor.execute(sql, (code,))
                results = cursor.fetchall()
                for result in results:
                    if result[0]:
                        rates.append(result[0])
            except Exception as e:
                print(f"查询分红数据失败: {e}")
            
            if not rates:
                return None
            
            # 计算近3年所有记录的平均值
            average_rate = sum(rates) / len(rates)
            
            return average_rate
            
        except Exception as e:
            print(f"获取A股分红率失败: {e}")
            return None


if __name__ == "__main__":
    # 测试
    a_stock_bonus_service = AStockBonusService()
    
    # 测试获取平均分红率
    stock_code = "600987"
    print(f"正在测试股票代码: {stock_code}")
    average_bonus_rate = a_stock_bonus_service.get_bonus_rate(stock_code)
    if average_bonus_rate is not None:
        print(f"A股 {stock_code} 的平均分红率: {average_bonus_rate:.2f}%")
    else:
        print(f"A股 {stock_code} 没有找到分红数据")
