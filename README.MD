# INSTALL

# python 源设置
## 设置全局镜像源为清华源
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

## 为了确保安全，通常需要添加信任主机，避免 SSL 证书问题
pip config set install.trusted-host pypi.tuna.tsinghua.edu.cn

## UV
1. uv venv
2. uv sync
3. source .venv/bin/activate
4. cd stocks
5. briefcase dev

## ENV PREPARE
1. uv add briefcase
2. uv add baostock
3. briefcase new .

## update akshare
1. pip install akshare --upgrade

## DEVELOP
1. briefcase dev

## BUILD EXE
1. briefcase create || briefcase update -r 
2. briefcase build 
3. briefcase run 

if you want to update, build, and run in one step, you could use `briefcase run -u -r`

## BUILD INSTALLER
1. briefcase package --adhoc-sign

## BUILD ANDROID
1. briefcase create/update android
2. briefcase build android 
3. briefcase run android

# REFERENCE
[beeware教程](https://docs.beeware.org/en/latest/tutorial/tutorial-0.html)  
[toga](https://toga.readthedocs.io/en/stable/)  
[beeware论坛](https://github.com/beeware/toga/discussions)  
[akshare数据源](https://akshare.akfamily.xyz/data/stock/stock.html#id122)  
[flet](https://flet.dev/docs/getting-started/async-apps)
[icon](https://www.freepik.com/search?format=search&iconType=standard&last_filter=query&last_value=refresh&query=refresh&type=icon)

# TODO

## 高优先级
1. **硬编码数据库路径** — `app.py:16` 写死了 `D:\Site\stock\finance.db`，无法在其他机器运行
2. **测试覆盖率为 0%** — `test_app.py` 只有 `assert 1+1==2`，没有任何业务逻辑测试
3. **SQL 注入风险** — `a_stock_service.py:64,341` 和 `hk_stock_service.py:187` 的 `ORDER BY` 子句使用 f-string 拼接不受信任的配置值
4. **无日志系统** — 整个项目用 `print()` 而非 logging，无法排查线上问题

## 中优先级
5. **`sys.path.append` hack** — 5 个服务文件都手动修改了 `sys.path`，正确的包结构不应需要
6. **默认配置重复** — `DEFAULT_STOCK_CONFIG` 在 `config_service.py` 和 `a_stock_config.py` 中重复定义，HK 配置同理
7. **HK 股票选择不完整** — `on_hk_stock_select()` 只改窗口标题，未像 A 股那样显示详情视图
8. **A/HK 视图代码重复** — `a_stock_list.py` 与 `hk_stock_list.py`、`a_stock_config.py` 与 `hk_stock_config.py` 高度相似，可抽取基类
9. **裸 `except:` 滥用** — `bonus.py`、`a_stock_service.py` 等多处捕获了 `SystemExit` 和 `KeyboardInterrupt`
10. **控制器职责过重** — `a_stock_controller.py` 同时管理 A 股/HK 股列表、配置、详情、任务，应拆分
11. **数据库连接管理薄弱** — 无连接池限制、无上下文管理器、print 和 logger 混用

## 低优先级
12. **东财 API 降级问题** — `a_stock_service.py:479` 有 `# todo 好像获取不到最新价`，`stock_zh_a_spot_em()` 可能缺列
13. **未使用的上下文管理器** — `ABonusService` 等类的 `__enter__`/`__exit__` 是空实现
14. **项目名称不一致** — 根 `pyproject.toml` 项目名 `stock2`，但包名是 `stocks`
15. **HK 财务表列名风格不一致** — 全大写 `SECURITY_CODE` vs A 股小写 `code`
16. **分红率硬编码截断** — `a_bonus_service.py:303` 硬编码 10%-90% 阈值且未记录
17. **提交信息无描述性** — 大量 "modify"、"mm" 提交

## 功能待实现
1. 现金占比
2. 经营性收入流和资本支出
