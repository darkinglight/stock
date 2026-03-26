from typing import Optional
from database.connection import DatabaseConnectionManager


class ConfigService:
    """配置服务 - 处理配置相关操作"""
    
    def __init__(self):
        """
        初始化配置服务
        """
        self.db_manager = DatabaseConnectionManager()
        self._init_config_table()
    
    def _init_config_table(self):
        """
        初始化配置表
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # 创建配置表，用于记录刷新时间
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,            -- 配置键
            value TEXT NOT NULL,             -- 配置值
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
    
    def set_config(self, key: str, value: str):
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
    
    def get_config(self, key: str) -> Optional[str]:
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
