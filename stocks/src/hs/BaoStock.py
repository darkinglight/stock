from collections import namedtuple

import baostock as bs
from stocks.SqliteTool import SqliteTool

Stock = namedtuple('Stock', ['code', 'name'])


def allstock():
    sqlite_tool = SqliteTool()
    select_sql = "select code, name from stock where status = 1 and name != '';"
    datas = sqlite_tool.query_many(select_sql)
    result = []
    for item in datas:
        stock = Stock(code=item[0], name=item[1])
        result.append(stock)
    return result


def init_all_stock():
    # 创建数据表info的SQL语句
    create_tb_sql = ("create table if not exists stock("
                     "code text primary key,"
                     "status int not null,"
                     "name text);")
    # 创建对象
    sqliteTool = SqliteTool()
    # 创建数据表
    sqliteTool.create_table(create_tb_sql)

    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:' + lg.error_code)
    print('login respond  error_msg:' + lg.error_msg)

    rs = bs.query_all_stock(day="2023-01-03")
    print('query_all_stock respond error_code:' + rs.error_code)
    print('query_all_stock respond  error_msg:' + rs.error_msg)
    while (rs.error_code == '0') & rs.next():
        item = rs.get_row_data()
        sqliteTool.operate_one('insert into stock values(?,?,?)',
                               (item[0], item[1], item[2]))
    bs.logout()


if __name__ == "__main__":
    # 查询数据
    init_all_stock()
    result_many = allstock()
    print(result_many[100].name)
