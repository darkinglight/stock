# 项目规则

## 测试文件组织规则

所有测试文件必须按照模块结构放置在 `tests/` 目录对应的子目录中：

```
tests/
├── test_database/      # 测试 src/database/ 模块
├── test_hk/            # 测试 src/hk/ 模块
├── test_hs/            # 测试 src/hs/ 模块
├── test_models/        # 测试 src/models/ 模块
├── test_services/      # 测试 src/services/ 模块
├── test_stocks/        # 测试 src/stocks/ 模块
├── test_utils/         # 测试 src/utils/ 模块
└── __init__.py
```

### 命名规范

- 测试目录命名：`test_<模块名>`
- 测试文件命名：`test_<被测试文件名>.py`

### 示例

- `src/database/base_repository.py` 的测试文件应放在 `tests/test_database/test_base_repository.py`
- `src/services/a_stock_service.py` 的测试文件应放在 `tests/test_services/test_a_stock_service.py`
- `src/stocks/app.py` 的测试文件应放在 `tests/test_stocks/test_app.py`

### 注意事项

- 不允许将测试文件直接放在 `tests/` 根目录下
- 每个测试子目录必须包含 `__init__.py` 文件
- 测试文件应与被测试的源代码保持同步的目录结构