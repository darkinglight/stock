import re
import akshare as ak
from typing import Dict, List, Optional, Tuple


class SmartApiFinder:
    """智能API查找器 - 可以根据用户需求自动查找、测试并添加接口到skill文档"""
    
    def __init__(self, api_file_path: str, skill_file_path: str):
        self.api_file_path = api_file_path
        self.skill_file_path = skill_file_path
        self.interfaces = self._parse_api_file()
        self.existing_interfaces = self._get_existing_interfaces()
    
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
    
    def _get_existing_interfaces(self) -> set:
        """从SKILL.md中获取已存在的接口列表"""
        existing = set()
        
        try:
            with open(self.skill_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找所有函数定义
            pattern = r'\*\*函数\*\*:\s*`(\w+)\(\)`'
            matches = re.findall(pattern, content)
            existing = set(matches)
        except FileNotFoundError:
            pass
        
        return existing
    
    def find_interface_by_keyword(self, keyword: str) -> List[str]:
        """根据关键词查找接口（排除已存在的）"""
        keyword = keyword.lower()
        matched_interfaces = []
        
        for interface_name, info in self.interfaces.items():
            # 排除已存在的接口
            if interface_name in self.existing_interfaces:
                continue
            
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
    
    def generate_skill_section(self, interface_name: str, info: Dict) -> str:
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
    
    def add_to_skill_md(self, section: str, section_title: str = "新增接口") -> bool:
        """将新接口文档添加到SKILL.md文件中"""
        with open(self.skill_file_path, 'r', encoding='utf-8') as f:
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
            
            with open(self.skill_file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"接口文档已成功添加到SKILL.md")
            return True
        else:
            print("未找到'参考文档'标记，无法插入")
            return False
    
    def auto_find_and_add(self, keyword: str, max_interfaces: int = 5) -> Dict:
        """自动查找、测试并添加接口
        
        返回: {
            'total_found': 总共找到的接口数,
            'tested': 测试的接口数,
            'successful': 成功的接口数,
            'added': 添加到skill的接口数,
            'interfaces': 接口详情列表
        }
        """
        print(f"正在搜索包含'{keyword}'的接口...")
        
        # 查找匹配的接口
        matched = self.find_interface_by_keyword(keyword)
        
        if not matched:
            return {
                'total_found': 0,
                'tested': 0,
                'successful': 0,
                'added': 0,
                'interfaces': [],
                'message': f"未找到包含'{keyword}'的接口"
            }
        
        print(f"找到 {len(matched)} 个匹配的接口（排除已存在的）")
        
        # 限制测试的接口数量
        matched = matched[:max_interfaces]
        
        # 测试接口
        results = []
        added_count = 0
        
        for interface_name in matched:
            print(f"\n测试接口: {interface_name}")
            success, message, sample = self.test_interface(interface_name)
            
            result = {
                'name': interface_name,
                'success': success,
                'message': message,
                'sample': sample if success else None
            }
            
            if success:
                print(f"✓ {message}")
                
                # 获取接口信息并添加到skill
                info = self.get_interface_info(interface_name)
                if info:
                    section = self.generate_skill_section(interface_name, info)
                    if self.add_to_skill_md(section):
                        added_count += 1
                        result['added'] = True
                        result['description'] = info['description']
            else:
                print(f"✗ {message}")
            
            results.append(result)
        
        return {
            'total_found': len(matched),
            'tested': len(matched),
            'successful': len([r for r in results if r['success']]),
            'added': added_count,
            'interfaces': results,
            'message': f"测试完成！成功添加 {added_count} 个接口到skill"
        }


def main():
    """主函数 - 演示如何使用"""
    api_file = "/Users/janet/Site/stock/.trae/skills/stock-query/api.txt"
    skill_file = "/Users/janet/Site/stock/.trae/skills/stock-query/SKILL.md"
    
    finder = SmartApiFinder(api_file, skill_file)
    
    print(f"总共找到 {len(finder.interfaces)} 个接口")
    print(f"已存在 {len(finder.existing_interfaces)} 个接口")
    
    # 示例：自动查找并添加估值相关接口
    keyword = "估值"
    result = finder.auto_find_and_add(keyword, max_interfaces=3)
    
    print(f"\n{result['message']}")
    print(f"总共找到: {result['total_found']}")
    print(f"测试通过: {result['successful']}")
    print(f"成功添加: {result['added']}")


if __name__ == "__main__":
    main()
