# INSTALL

## ENV PREPARE
1. python -m pip install briefcase
2. briefcase new .

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
[beeware论坛](https://github.com/beeware/toga/discussions)  
[akshare数据源](https://akshare.akfamily.xyz/data/stock/stock.html#id122)  
