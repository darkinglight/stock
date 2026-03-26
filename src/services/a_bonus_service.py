import akshare as ak
from typing import Optional, List
import datetime
from database.connection import DatabaseConnectionManager
from models import Bonus


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
        update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    
    SQL_GET_DIVIDEND_RATES = '''
    SELECT dividend_payout_rate FROM bonus 
    WHERE stock_code = ?
    '''
    
    def __init__(self):
        """初始化服务"""
        self.db_manager = DatabaseConnectionManager()
        self.config_service = ConfigService()
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
        except Exception as e:
            print(f"关闭数据库连接失败: {e}")

    def _create_bonus_table(self):
        """创建分红记录表"""
        try:
            self.cursor.execute(self.SQL_CREATE_BONUS_TABLE)
            self.conn.commit()
        except Exception as e:
            print(f"创建表失败: {e}")
    
    def _get_last_update_time(self, code: str) -> Optional[datetime.datetime]:
        """获取上次更新时间"""
        try:
            self.cursor.execute(self.SQL_GET_LAST_UPDATE_TIME, (code,))
            result = self.cursor.fetchone()
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
            # 更新配置中的最后更新时间
            self.config_service.set_config(f"bonus_{code}", str(int(datetime.datetime.now().timestamp())))
        except Exception as e:
            print(f"保存分红记录失败: {e}")
            try:
                self.conn.rollback()
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
            sql = self.SQL_GET_DIVIDEND_RATES
            
            rates = []
            try:
                self.cursor.execute(sql, (code,))
                results = self.cursor.fetchall()
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
    a_bonus_service = ABonusService()
    
    # 测试获取平均分红率
    stock_code = "600987"
    print(f"正在测试股票代码: {stock_code}")
    average_bonus_rate = a_bonus_service.get_bonus_rate(stock_code)
    if average_bonus_rate is not None:
        print(f"A股 {stock_code} 的平均分红率: {average_bonus_rate:.2f}%")
    else:
        print(f"A股 {stock_code} 没有找到分红数据")
