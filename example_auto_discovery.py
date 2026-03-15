"""
示例：如何在AI助手中使用智能API查找器

这个示例展示了当用户需要查询某个数据时，如果当前skill中没有对应接口，
如何使用智能查找器自动查找、测试并添加新接口。
"""

from smart_api_finder import SmartApiFinder
import akshare as ak
import re


def extract_keyword_from_query(query: str) -> str:
    """从用户查询中提取关键词"""
    # 常见的关键词映射
    keyword_map = {
        '估值': ['估值', '市盈率', '市净率', 'pe', 'pb'],
        '分红': ['分红', '派息', '股息', '红利'],
        '财务': ['财务', '财报', '利润表', '资产负债表', '现金流量表'],
        '行情': ['行情', '股价', '实时', '最新价'],
        '历史': ['历史', '过去', '历史数据'],
        '行业': ['行业', '板块', '行业板块'],
        '概念': ['概念', '概念板块'],
        '新股': ['新股', 'ipo', '申购'],
        '业绩': ['业绩', '季报', '年报', '三季报'],
        '公告': ['公告', '披露'],
        '资金': ['资金', '主力', '资金流向'],
    }
    
    query_lower = query.lower()
    
    for keyword, patterns in keyword_map.items():
        for pattern in patterns:
            if pattern in query_lower:
                return keyword
    
    # 如果没有匹配到，尝试提取第一个有意义的词
    words = re.findall(r'[\u4e00-\u9fa5]{2,}', query)
    if words:
        return words[0]
    
    return query


def try_existing_interfaces(query: str) -> dict:
    """尝试使用现有接口查询数据"""
    print(f"尝试使用现有接口查询: {query}")
    
    # 这里应该有逻辑来匹配用户查询和现有接口
    # 简化示例，假设我们检查了但没有找到合适的接口
    return None


def try_new_interfaces(query: str, interfaces: list) -> dict:
    """尝试使用新添加的接口查询数据"""
    print(f"尝试使用新接口查询: {query}")
    
    for interface_info in interfaces:
        if interface_info['success'] and interface_info.get('added'):
            interface_name = interface_info['name']
            print(f"使用接口: {interface_name}")
            
            try:
                # 调用接口
                func = getattr(ak, interface_name)
                result = func()
                return {
                    'interface': interface_name,
                    'data': result,
                    'success': True
                }
            except Exception as e:
                print(f"接口调用失败: {e}")
                continue
    
    return None


def query_stock_data_with_auto_discovery(query: str):
    """
    智能查询股票数据
    
    流程：
    1. 尝试使用现有接口查询
    2. 如果没有找到，使用智能查找器查找相关接口
    3. 测试并添加新接口到skill
    4. 使用新接口查询数据
    """
    api_file = "/Users/janet/Site/stock/.trae/skills/stock-query/api.txt"
    skill_file = "/Users/janet/Site/stock/.trae/skills/stock-query/SKILL.md"
    
    print(f"用户查询: {query}")
    print("=" * 60)
    
    # 步骤1: 尝试使用现有接口
    print("\n步骤1: 尝试使用现有接口...")
    result = try_existing_interfaces(query)
    
    if result:
        print("✓ 找到现有接口并成功查询")
        return result
    
    print("✗ 未找到合适的现有接口")
    
    # 步骤2: 提取关键词
    print("\n步骤2: 提取关键词...")
    keyword = extract_keyword_from_query(query)
    print(f"关键词: {keyword}")
    
    # 步骤3: 使用智能查找器查找并添加接口
    print("\n步骤3: 使用智能查找器查找并添加接口...")
    finder = SmartApiFinder(api_file, skill_file)
    find_result = finder.auto_find_and_add(keyword, max_interfaces=3)
    
    print(f"\n查找结果:")
    print(f"  总共找到: {find_result['total_found']}")
    print(f"  测试通过: {find_result['successful']}")
    print(f"  成功添加: {find_result['added']}")
    
    # 步骤4: 使用新接口查询
    if find_result['added'] > 0:
        print("\n步骤4: 使用新接口查询数据...")
        result = try_new_interfaces(query, find_result['interfaces'])
        
        if result:
            print("✓ 使用新接口成功查询")
            return result
    
    print("\n✗ 未能获取数据")
    return None


def main():
    """主函数 - 演示使用示例"""
    
    # 示例1: 查询分红数据
    print("\n" + "=" * 60)
    print("示例1: 查询分红数据")
    print("=" * 60)
    
    query1 = "查询贵州茅台的分红记录"
    result1 = query_stock_data_with_auto_discovery(query1)
    
    if result1:
        print(f"\n查询成功！使用接口: {result1['interface']}")
        print(f"数据示例:\n{result1['data'].head() if hasattr(result1['data'], 'head') else result1['data']}")
    
    # 示例2: 查询估值数据
    print("\n\n" + "=" * 60)
    print("示例2: 查询估值数据")
    print("=" * 60)
    
    query2 = "查询平安银行的估值指标"
    result2 = query_stock_data_with_auto_discovery(query2)
    
    if result2:
        print(f"\n查询成功！使用接口: {result2['interface']}")
        print(f"数据示例:\n{result2['data'].head() if hasattr(result2['data'], 'head') else result2['data']}")


if __name__ == "__main__":
    main()
