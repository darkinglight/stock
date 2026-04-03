# INSTALL

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
1. 现金占比
2. 经营性收入流和资本支出
3. roe方差稳定性