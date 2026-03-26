from typing import Optional
from database.connection import DatabaseConnectionManager


class ConfigService:
    """配置服务 - 处理配置相关操作"""
    
    def __init__(self):
        """
        初始化配置服务
        """
        self.db_manager = DatabaseConnectionManager()
        # 在初始化时获取数据库连接
        self.conn = self.db_manager.get_connection()
        self.cursor = self.conn.cursor()
        self._init_config_table()
    
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
    
    def _init_config_table(self):
        """
        初始化配置表
        """
        # 创建配置表，用于记录刷新时间
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,            -- 配置键
            value TEXT NOT NULL,             -- 配置值
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        self.conn.commit()
    
    def set_config(self, key: str, value: str):
        """
        设置配置
        :param key: 配置键
        :param value: 配置值
        """
        try:
            self.cursor.execute('''
            INSERT INTO config (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value=excluded.value,
                updated_at=CURRENT_TIMESTAMP
            ''', (key, value))
            
            self.conn.commit()
        except Exception as e:
            print(f"设置配置失败: {e}")
    
    def get_config(self, key: str) -> Optional[str]:
        """
        获取配置
        :param key: 配置键
        :return: 配置值，不存在返回None
        """
        try:
            self.cursor.execute('SELECT value FROM config WHERE key = ?', (key,))
            result = self.cursor.fetchone()
            
            if result and result[0]:
                return result[0]
            return None
        except Exception as e:
            print(f"获取配置失败: {e}")
            return None
    
    def get_last_refresh_time(self, key: str) -> Optional[float]:
        """
        获取上次刷新时间
        :param key: 配置键
        :return: 上次刷新时间的时间戳，None表示未刷新过
        """
        try:
            value = self.get_config(key)
            if value:
                return float(value)
            return None
        except Exception as e:
            print(f"获取上次刷新时间失败: {e}")
            return None
