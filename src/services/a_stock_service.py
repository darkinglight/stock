from typing import List, Optional
import time
from src.models.stock import Stock
from src.services.base_stock_service import BaseStockService


class AStockService(BaseStockService):
    """A股服务 - 处理A股数据"""
    
    def __init__(self):
        """
        初始化A股服务
        """
        super().__init__()
        self.refresh_config_key = "a_stock_last_refresh"

    def _get_all_stocks(self) -> List[Stock]:
        """
        获取所有A股
        :return: 股票列表
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT code, name, market, price, pe, pb, bonus_rate, market_cap, created_at, updated_at FROM stock WHERE market IN (?, ?, ?)', ('sh', 'sz', 'bj'))
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
                    market_cap=row[7],
                    created_at=row[8],
                    updated_at=row[9]
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
            
            cursor.execute('SELECT code, name, market, price, pe, pb, bonus_rate, market_cap, created_at, updated_at FROM stock WHERE code = ? AND market IN (?, ?, ?)', (code, 'sh', 'sz', 'bj'))
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
                    market_cap=row[7],
                    created_at=row[8],
                    updated_at=row[9]
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
    
    def get_financial_data(self, code: str) -> Optional[dict]:
        """
        获取股票财报数据
        :param code: 股票代码
        :return: 财报数据字典，包含：
            - roe: 最近4个季度ROE总和
            - bonus_rate: 分红率
            - pb: 市净率
            - debt_ratio: 资产负债率
        """
        import akshare as ak
        
        try:
            # 获取财务摘要数据
            stock_financial_abstract_df = ak.stock_financial_abstract(symbol=code)
            
            # 初始化结果字典
            financial_data = {
                'roe': 0.0,
                'bonus_rate': 0.0,
                'pb': 0.0,
                'debt_ratio': 0.0
            }
            
            # 提取ROE数据（最近4个季度）
            roe_values = []
            for _, row in stock_financial_abstract_df.iterrows():
                if row['指标'] == '净资产收益率(ROE)':
                    # 获取最近4个季度的数据
                    for col in ['20250930', '20250630', '20250331', '20241231']:
                        if col in stock_financial_abstract_df.columns:
                            value = row[col]
                            if value is not None and not isinstance(value, str):
                                try:
                                    roe_values.append(float(value))
                                except:
                                    pass
                    break
            
            # 计算最近4个季度ROE总和
            if roe_values:
                financial_data['roe'] = sum(roe_values[:4])
            
            # 提取分红率
            for _, row in stock_financial_abstract_df.iterrows():
                if row['指标'] == '分红率':
                    # 获取最新季度的分红率
                    for col in ['20250930', '20250630', '20250331', '20241231']:
                        if col in stock_financial_abstract_df.columns:
                            value = row[col]
                            if value is not None and not isinstance(value, str):
                                try:
                                    financial_data['bonus_rate'] = float(value)
                                    break
                                except:
                                    pass
                    break
            
            # 提取市净率
            for _, row in stock_financial_abstract_df.iterrows():
                if row['指标'] == '市净率':
                    # 获取最新季度的市净率
                    for col in ['20250930', '20250630', '20250331', '20241231']:
                        if col in stock_financial_abstract_df.columns:
                            value = row[col]
                            if value is not None and not isinstance(value, str):
                                try:
                                    financial_data['pb'] = float(value)
                                    break
                                except:
                                    pass
                    break
            
            # 提取资产负债率
            for _, row in stock_financial_abstract_df.iterrows():
                if row['指标'] == '资产负债率':
                    # 获取最新季度的资产负债率
                    for col in ['20250930', '20250630', '20250331', '20241231']:
                        if col in stock_financial_abstract_df.columns:
                            value = row[col]
                            if value is not None and not isinstance(value, str):
                                try:
                                    financial_data['debt_ratio'] = float(value)
                                    break
                                except:
                                    pass
                    break
            
            return financial_data
            
        except Exception as e:
            print(f"获取财报数据失败: {e}")
            return None
