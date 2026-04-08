import json
import sqlite3
from typing import Optional, Dict, Any
from database.connection import DatabaseConnectionManager


class ConfigService:
    """配置服务 - 处理配置相关操作"""

    # 股票列表配置键名
    STOCK_LIST_CONFIG_KEY = 'stock_list_config'

    # 默认配置
    DEFAULT_STOCK_CONFIG = {
        'page_size': 20,
        'max_debt_ratio': 30.0,
        'min_pe': 3,
        'max_pe': 20,
        'min_pb': 0.5,
        'max_pb': 5,
        'min_roe': 5,
        'max_roe': 30,
        'min_roe_stability': 50,
        'max_roe_stability': 100,
        'min_roe_trend': -100,
        'max_roe_trend': 100,
        'min_bonus_rate': 10,
        'max_bonus_rate': 100,
        'sort_by': 'growth / pb',
        'sort_order': 'desc'
    }

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

    def save_stock_list_config(self, config: Dict[str, Any]):
        """
        保存股票列表配置
        :param config: 配置字典
        """
        try:
            config_json = json.dumps(config, ensure_ascii=False)
            self.set_config(self.STOCK_LIST_CONFIG_KEY, config_json)
        except Exception as e:
            print(f"保存股票列表配置失败: {e}")

    def load_stock_list_config(self) -> Dict[str, Any]:
        """
        加载股票列表配置
        :return: 配置字典，如果不存在返回默认配置
        """
        try:
            config_json = self.get_config(self.STOCK_LIST_CONFIG_KEY)
            if config_json:
                config = json.loads(config_json)
                # 合并默认配置，确保所有字段都存在
                merged_config = self.DEFAULT_STOCK_CONFIG.copy()
                merged_config.update(config)
                return merged_config
            return self.DEFAULT_STOCK_CONFIG.copy()
        except Exception as e:
            print(f"加载股票列表配置失败: {e}")
            return self.DEFAULT_STOCK_CONFIG.copy()
