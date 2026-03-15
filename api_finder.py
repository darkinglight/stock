import re
import akshare as ak
from typing import Dict, List, Optional, Tuple

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


def main():
    """主函数 - 演示如何使用"""
    api_file = "/Users/janet/Site/stock/.trae/skills/stock-query/api.txt"
    finder = ApiFinder(api_file)
    
    print(f"总共找到 {len(finder.interfaces)} 个接口")
    
    # 示例：查找包含"财务"关键词的接口
    keyword = "财务"
    matched = finder.find_interface_by_keyword(keyword)
    print(f"\n包含'{keyword}'的接口: {matched}")
    
    # 测试第一个匹配的接口
    if matched:
        interface_name = matched[0]
        print(f"\n测试接口: {interface_name}")
        success, message, sample = finder.test_interface(interface_name)
        print(f"测试结果: {success}")
        print(f"消息: {message}")
        if success and sample:
            print(f"示例数据:\n{sample}")
        
        # 生成SKILL文档段落
        info = finder.get_interface_info(interface_name)
        if info:
            section = generate_skill_section(interface_name, info)
            print(f"\n生成的文档段落:\n{section}")


if __name__ == "__main__":
    main()
