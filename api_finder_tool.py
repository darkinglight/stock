import re
import akshare as ak
from typing import Dict, List, Optional, Tuple
import sys


class ApiFinder:
    def __init__(self, api_file_path: str):
        self.api_file_path = api_file_path
        self.interfaces = self._parse_api_file()
    
    def _parse_api_file(self) -> Dict[str, Dict]:
        """解析api.txt文件，提取所有接口信息"""
        interfaces = {}
        
        with open(self.api_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 使用正则表达式匹配接口块
        pattern = r'接口:\s*(\w+)\s*\n目标地址:.*?\n描述:\s*(.*?)\s*\n限量:\s*(.*?)\s*\n输入参数.*?接口示例.*?```python\n(.*?)```'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for match in matches:
            interface_name, description, limit, example = match
            interfaces[interface_name] = {
                'description': description.strip(),
                'limit': limit.strip(),
                'example': example.strip()
            }
        
        return interfaces
    
    def find_interface_by_keyword(self, keyword: str) -> List[str]:
        """根据关键词查找接口"""
        keyword = keyword.lower()
        matched_interfaces = []
        
        for interface_name, info in self.interfaces.items():
            if keyword in interface_name.lower() or keyword in info['description'].lower():
                matched_interfaces.append(interface_name)
        
        return matched_interfaces
    
    def test_interface(self, interface_name: str) -> Tuple[bool, str, Optional[str]]:
        """测试接口是否可以正常工作
        
        返回: (是否成功, 错误信息/数据信息, 示例数据)
        """
        try:
            # 获取接口函数
            func = getattr(ak, interface_name)
            
            # 尝试调用接口（使用默认参数或最小参数）
            result = func()
            
            # 检查返回结果
            if hasattr(result, 'empty') and result.empty:
                return False, "接口返回空数据", None
            
            # 获取前几行作为示例
            if hasattr(result, 'head'):
                sample = str(result.head(3))
            else:
                sample = str(result)[:500]
            
            return True, "接口测试成功", sample
            
        except AttributeError:
            return False, f"接口 {interface_name} 不存在", None
        except Exception as e:
            return False, f"接口调用失败: {str(e)}", None
    
    def get_interface_info(self, interface_name: str) -> Optional[Dict]:
        """获取接口的详细信息"""
        return self.interfaces.get(interface_name)
    
    def list_all_interfaces(self) -> List[str]:
        """列出所有接口名称"""
        return list(self.interfaces.keys())


def generate_skill_section(interface_name: str, info: Dict) -> str:
    """生成SKILL.md中的接口文档段落"""
    section = f"""
#### 新增接口: {interface_name}
{info['description']}

**函数**: `{interface_name}()`

**限量**: {info['limit']}

**使用示例**:
```python
import akshare as ak

# {info['description']}
result = ak.{interface_name}()
print(result)
```

**注意**: 此接口从api.txt中自动添加，已验证可以正常使用。

---
"""
    return section


def add_to_skill_md(skill_file_path: str, section: str, section_title: str = "新增接口"):
    """将新接口文档添加到SKILL.md文件中"""
    with open(skill_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经存在该接口
    if section in content:
        print(f"接口文档已存在于SKILL.md中")
        return False
    
    # 在"参考文档"之前添加新接口
    marker = "## 参考文档"
    if marker in content:
        # 找到合适的位置插入
        insert_position = content.find(marker)
        
        # 检查是否已经有"新增接口"章节
        new_section_marker = f"### {section_title}"
        if new_section_marker in content:
            # 在现有"新增接口"章节后添加
            insert_position = content.find(new_section_marker) + len(new_section_marker)
            new_content = content[:insert_position] + "\n" + section + content[insert_position:]
        else:
            # 创建新的"新增接口"章节
            new_section_header = f"\n\n### {section_title}\n\n以下接口从api.txt中自动添加，已验证可以正常使用：\n"
            new_content = content[:insert_position] + new_section_header + section + "\n" + content[insert_position:]
        
        with open(skill_file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"接口文档已成功添加到SKILL.md")
        return True
    else:
        print("未找到'参考文档'标记，无法插入")
        return False


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python3 api_finder_tool.py <关键词> [测试并添加]")
        print("示例: python3 api_finder_tool.py 财务")
        print("示例: python3 api_finder_tool.py 财务 --add")
        return
    
    keyword = sys.argv[1]
    should_add = '--add' in sys.argv
    
    api_file = "/Users/janet/Site/stock/.trae/skills/stock-query/api.txt"
    skill_file = "/Users/janet/Site/stock/.trae/skills/stock-query/SKILL.md"
    
    finder = ApiFinder(api_file)
    
    print(f"总共找到 {len(finder.interfaces)} 个接口")
    print(f"正在搜索包含'{keyword}'的接口...")
    
    # 查找匹配的接口
    matched = finder.find_interface_by_keyword(keyword)
    
    if not matched:
        print(f"未找到包含'{keyword}'的接口")
        return
    
    print(f"\n找到 {len(matched)} 个匹配的接口:")
    for i, interface_name in enumerate(matched, 1):
        info = finder.get_interface_info(interface_name)
        print(f"{i}. {interface_name} - {info['description'][:50]}...")
    
    # 测试接口
    print(f"\n开始测试接口...")
    working_interfaces = []
    
    for interface_name in matched:
        print(f"\n测试接口: {interface_name}")
        success, message, sample = finder.test_interface(interface_name)
        
        if success:
            print(f"✓ {message}")
            working_interfaces.append(interface_name)
            
            # 如果需要添加到SKILL.md
            if should_add:
                info = finder.get_interface_info(interface_name)
                section = generate_skill_section(interface_name, info)
                add_to_skill_md(skill_file, section)
        else:
            print(f"✗ {message}")
    
    print(f"\n测试完成！")
    print(f"可用接口: {len(working_interfaces)}/{len(matched)}")
    
    if working_interfaces:
        print(f"\n可用接口列表:")
        for interface_name in working_interfaces:
            print(f"  - {interface_name}")


if __name__ == "__main__":
    main()
