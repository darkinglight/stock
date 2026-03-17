# Documentation Index

## 项目文档

欢迎查阅股票项目的完整文档。本文档提供了所有文档的索引和简要说明。

## 📚 文档列表

### 1. [ARCHITECTURE.md](ARCHITECTURE.md)
**架构设计文档**

详细描述了项目的整体架构设计，包括：

- **项目概述**: 项目背景和目标
- **架构设计原则**: 数据库连接管理、模块化设计、分层架构
- **目录结构**: 完整的项目文件组织结构
- **核心组件设计**: 数据库连接管理器、基础仓储类、模块仓储接口
- **数据流设计**: 数据获取和更新流程
- **数据库设计**: 表结构和优化策略
- **扩展性设计**: 如何新增市场模块和数据源
- **性能优化策略**: 数据库、应用、UI层面的优化
- **安全性考虑**: 数据安全和API安全
- **测试策略**: 单元测试、集成测试、UI测试
- **部署和发布**: 开发环境和构建发布流程
- **迁移计划**: 从现有架构迁移到新架构的步骤

**适合人群**: 架构师、技术负责人、高级开发者

---

### 2. [DATABASE.md](DATABASE.md)
**数据库设计文档**

详细描述了数据库的设计和管理，包括：

- **数据库概述**: SQLite数据库的使用和配置
- **数据库连接管理**: DatabaseConnectionManager的设计和使用
- **连接生命周期**: 创建、使用、释放的完整流程
- **数据表设计**: 
  - A股模块表 (a_stock, a_detail, a_financial, a_indicator)
  - H股模块表 (h_stock, h_financial, h_report)
- **数据库优化策略**: 索引优化、查询优化、事务管理
- **数据维护**: 定期清理、VACUUM、ANALYZE
- **数据迁移策略**: 版本管理和迁移脚本
- **数据备份与恢复**: 备份策略和恢复方案
- **性能监控**: 监控指标和优化建议
- **安全性考虑**: 数据加密、访问控制、数据验证

**适合人群**: 数据库管理员、后端开发者

---

### 3. [MIGRATION.md](MIGRATION.md)
**迁移指南**

详细描述了如何从现有架构迁移到新架构，包括：

- **迁移目标**: 明确迁移的目的和预期效果
- **迁移前准备**: 备份、依赖检查、测试运行
- **迁移步骤**: 
  - 第一阶段：创建新的目录结构
  - 第二阶段：重构数据库连接管理
  - 第三阶段：重构A股模块
  - 第四阶段：重构H股模块
  - 第五阶段：更新主应用代码
  - 第六阶段：测试和优化
- **迁移验证**: 功能验证、性能验证、代码质量验证
- **回滚计划**: 出现问题时的回滚步骤
- **后续优化**: 缓存机制、异步支持、日志监控

**适合人群**: 项目负责人、开发者

---

### 4. [QUICK_START.md](QUICK_START.md)
**快速开始指南**

帮助开发者快速理解和使用新架构，包括：

- **核心概念**: 
  - 数据库连接管理
  - 基础仓储类
  - 模块化设计
  - 分层架构
- **快速示例**:
  - 示例1：创建新的数据仓储
  - 示例2：创建新的视图
  - 示例3：在主应用中使用
- **常见任务**:
  - 添加新的股票市场模块
  - 优化数据库查询
  - 添加数据缓存
- **性能优化建议**: 批量操作、使用索引、连接复用
- **测试建议**: 单元测试、集成测试
- **调试技巧**: 日志、连接状态、性能分析
- **TDD 实践**: 测试驱动开发的完整流程和示例

**适合人群**: 新加入的开发者、需要快速上手的开发者

---

### 5. [TDD.md](TDD.md)
**测试驱动开发指南**

详细描述了如何在项目中实施测试驱动开发（TDD）方法论，包括：

- **TDD 核心理念**: 什么是 TDD 和 TDD 的好处
- **TDD 开发循环**: 红-绿-重构的详细步骤
- **TDD 实施原则**: 
  - 先写测试，后写代码
  - 小步快跑
  - 持续重构
  - 测试覆盖
- **TDD 实践示例**:
  - 示例1：数据库连接管理器
  - 示例2：股票仓储类
- **测试覆盖率要求**: 单元测试、集成测试、关键路径覆盖率
- **运行测试**: 各种测试运行命令和选项
- **持续集成**: 提交前检查、预提交钩子
- **常见问题**: 外部依赖、异步代码、UI 组件测试

**适合人群**: 所有开发者、测试工程师

---

## 🎯 按角色推荐阅读

### 架构师 / 技术负责人
1. [ARCHITECTURE.md](ARCHITECTURE.md) - 了解整体架构设计
2. [DATABASE.md](DATABASE.md) - 了解数据库设计
3. [MIGRATION.md](MIGRATION.md) - 了解迁移计划

### 后端开发者
1. [DATABASE.md](DATABASE.md) - 了解数据库设计和管理
2. [QUICK_START.md](QUICK_START.md) - 快速开始开发
3. [ARCHITECTURE.md](ARCHITECTURE.md) - 了解架构设计原则
4. [TDD.md](TDD.md) - 学习测试驱动开发

### 前端开发者
1. [QUICK_START.md](QUICK_START.md) - 了解视图层设计
2. [ARCHITECTURE.md](ARCHITECTURE.md) - 了解分层架构
3. [MIGRATION.md](MIGRATION.md) - 了解迁移步骤
4. [TDD.md](TDD.md) - 学习测试驱动开发

### 新加入的开发者
1. [QUICK_START.md](QUICK_START.md) - 快速上手
2. [ARCHITECTURE.md](ARCHITECTURE.md) - 了解项目架构
3. [DATABASE.md](DATABASE.md) - 了解数据库设计
4. [TDD.md](TDD.md) - 学习测试驱动开发

### 项目负责人
1. [MIGRATION.md](MIGRATION.md) - 了解迁移计划
2. [ARCHITECTURE.md](ARCHITECTURE.md) - 了解架构设计
3. [DATABASE.md](DATABASE.md) - 了解数据库设计
4. [TDD.md](TDD.md) - 了解测试驱动开发

---

## 📖 按任务推荐阅读

### 理解项目架构
- [ARCHITECTURE.md](ARCHITECTURE.md) - 完整的架构设计文档

### 设计数据库
- [DATABASE.md](DATABASE.md) - 数据库设计文档

### 迁移现有代码
- [MIGRATION.md](MIGRATION.md) - 详细的迁移指南

### 快速开始开发
- [QUICK_START.md](QUICK_START.md) - 快速开始指南

### 优化性能
- [ARCHITECTURE.md](ARCHITECTURE.md) - 性能优化策略
- [DATABASE.md](DATABASE.md) - 数据库优化策略
- [QUICK_START.md](QUICK_START.md) - 性能优化建议

### 添加新功能
- [QUICK_START.md](QUICK_START.md) - 快速示例
- [ARCHITECTURE.md](ARCHITECTURE.md) - 扩展性设计

### 测试和调试
- [QUICK_START.md](QUICK_START.md) - 测试建议和调试技巧
- [ARCHITECTURE.md](ARCHITECTURE.md) - 测试策略
- [TDD.md](TDD.md) - 测试驱动开发完整指南

---

## 🔗 相关资源

### 项目文件
- `README.MD` - 项目介绍和安装说明
- `pyproject.toml` - 项目依赖和配置
- `tests/` - 测试用例

### 源代码
- `src/database/` - 数据库管理
- `src/a_stock/` - A股模块
- `src/h_stock/` - H股模块
- `src/ui/` - UI模块
- `src/utils/` - 工具模块

### 外部资源
- [Toga 文档](https://toga.readthedocs.io/)
- [AkShare 文档](https://akshare.akfamily.xyz/)
- [Briefcase 文档](https://briefcase.readthedocs.io/)

---

## 📝 文档更新记录

### 2025-03-17
- 创建架构设计文档 (ARCHITECTURE.md)
- 创建数据库设计文档 (DATABASE.md)
- 创建迁移指南 (MIGRATION.md)
- 创建快速开始指南 (QUICK_START.md)
- 创建测试驱动开发指南 (TDD.md)
- 创建文档索引 (INDEX.md)

---

## 💡 使用建议

1. **首次阅读**: 建议按照 QUICK_START → ARCHITECTURE → DATABASE 的顺序阅读
2. **开发参考**: 开发时可以随时查阅 QUICK_START 中的示例
3. **架构决策**: 重要的架构决策参考 ARCHITECTURE.md
4. **数据库操作**: 数据库相关操作参考 DATABASE.md
5. **代码迁移**: 迁移现有代码时参考 MIGRATION.md

---

## 🤝 贡献文档

如果您发现文档有错误或需要补充，请：

1. 在项目中创建 Issue 描述问题
2. 提交 Pull Request 改进文档
3. 确保文档格式统一、内容准确

---

## 📧 获取帮助

如果您在阅读文档或使用项目时遇到问题：

1. 查阅本文档索引，找到相关文档
2. 查看项目源代码中的注释
3. 查看测试用例了解使用方法
4. 提交 Issue 寻求帮助

---

**最后更新**: 2025-03-17  
**文档版本**: 1.0.0