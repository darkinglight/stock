# 智能API查找器使用说明

## 功能介绍

智能API查找器（SmartApiFinder）可以自动从api.txt中查找、测试并添加接口到SKILL.md文档中。

## 主要特性

1. **自动查找**：根据关键词从api.txt中查找相关接口
2. **智能过滤**：自动排除已在SKILL.md中存在的接口
3. **接口测试**：自动测试接口是否可以正常工作
4. **自动添加**：将测试通过的接口自动添加到SKILL.md文档中
5. **错误处理**：跳过测试失败的接口，只添加可用的接口

## 使用方法

### 方法1：直接使用Python脚本

```python
from smart_api_finder import SmartApiFinder

# 初始化查找器
api_file = "/Users/janet/Site/stock/.trae/skills/stock-query/api.txt"
skill_file = "/Users/janet/Site/stock/.trae/skills/stock-query/SKILL.md"
finder = SmartApiFinder(api_file, skill_file)

# 自动查找并添加接口
keyword = "分红"
result = finder.auto_find_and_add(keyword, max_interfaces=3)

print(result['message'])
print(f"总共找到: {result['total_found']}")
print(f"测试通过: {result['successful']}")
print(f"成功添加: {result['added']}")
```

### 方法2：使用命令行工具

```bash
# 查找接口（不添加到skill）
python3 api_finder_tool.py <关键词>

# 查找并添加接口到skill
python3 api_finder_tool.py <关键词> --add
```

### 方法3：在AI助手中使用

当用户需要查询某个数据时，如果当前skill中没有对应接口，可以：

1. 使用SmartApiFinder查找相关接口
2. 测试接口是否可用
3. 将可用接口添加到skill
4. 使用新接口获取数据

## 示例

### 示例1：查找估值相关接口

```python
from smart_api_finder import SmartApiFinder

finder = SmartApiFinder(api_file, skill_file)

# 查找估值接口
result = finder.auto_find_and_add("估值", max_interfaces=5)

# 查看结果
for interface in result['interfaces']:
    if interface['success']:
        print(f"✓ {interface['name']}: {interface['description']}")
    else:
        print(f"✗ {interface['name']}: {interface['message']}")
```

### 示例2：查找分红相关接口

```python
from smart_api_finder import SmartApiFinder

finder = SmartApiFinder(api_file, skill_file)

# 查找分红接口
result = finder.auto_find_and_add("分红", max_interfaces=3)

print(f"成功添加 {result['added']} 个接口")
```

### 示例3：查找财务相关接口

```python
from smart_api_finder import SmartApiFinder

finder = SmartApiFinder(api_file, skill_file)

# 查找财务接口
result = finder.auto_find_and_add("财务", max_interfaces=5)

print(f"测试通过: {result['successful']}/{result['tested']}")
```

## 常用关键词

以下是一些常用的搜索关键词：

- **估值**: 估值数据、估值比较
- **分红**: 分红派息、分红记录
- **财务**: 财务报表、财务指标
- **行情**: 实时行情、历史行情
- **行业**: 行业板块、行业对比
- **概念**: 概念板块、概念成分股
- **新股**: 新股发行、新股申购
- **业绩**: 业绩快报、业绩报表
- **公告**: 公司公告、公告披露
- **资金**: 资金流向、主力资金

## 注意事项

1. **接口测试**：不是所有接口都能正常工作，有些接口可能因为网络问题或数据源问题而失败
2. **重复添加**：工具会自动检测并跳过已在SKILL.md中存在的接口
3. **测试限制**：建议每次测试不超过5个接口，避免测试时间过长
4. **网络要求**：测试接口需要网络连接，确保网络畅通

## 返回结果说明

`auto_find_and_add()` 方法返回一个字典，包含以下字段：

- `total_found`: 找到的匹配接口数量（排除已存在的）
- `tested`: 测试的接口数量
- `successful`: 测试通过的接口数量
- `added`: 成功添加到skill的接口数量
- `interfaces`: 接口详情列表，每个接口包含：
  - `name`: 接口名称
  - `success`: 是否测试成功
  - `message`: 成功或失败的消息
  - `sample`: 示例数据（仅成功时）
  - `description`: 接口描述（仅添加成功时）
  - `added`: 是否已添加到skill（仅成功时）
- `message`: 总体消息

## 集成到AI助手

在AI助手中，可以这样集成：

```python
def query_stock_data(user_query):
    # 1. 尝试使用现有接口查询
    result = try_existing_interfaces(user_query)
    
    if result:
        return result
    
    # 2. 如果没有找到，使用智能查找器
    finder = SmartApiFinder(api_file, skill_file)
    keyword = extract_keyword(user_query)
    
    # 3. 查找并添加新接口
    find_result = finder.auto_find_and_add(keyword, max_interfaces=3)
    
    # 4. 使用新接口查询
    if find_result['added'] > 0:
        result = try_new_interfaces(user_query, find_result['interfaces'])
        return result
    
    return "未找到相关接口"
```

## 文件说明

- `smart_api_finder.py`: 主要的智能查找器类
- `api_finder_tool.py`: 命令行工具
- `api_finder.py`: 基础查找器类（用于测试）

## 更新日志

- v1.0: 初始版本，支持自动查找、测试和添加接口
- 支持排除已存在的接口
- 支持批量测试和添加
- 提供详细的测试结果和错误信息
