from collections import namedtuple
import baostock as bs
from stocks.SqliteTool import SqliteTool

PriceInfo = namedtuple("PriceInfo",
                       ['code', 'date', 'price', 'pe', 'pb'])

def priceinfo(code, date):
    dto = priceinfo_from_db(code, date)
    if dto is None:
        dto = priceinfo_from_api(code, date)
    return dto

def priceinfo_from_db(code, date):
    sqliteTool = SqliteTool()
    data = sqliteTool.query_one("select * from priceinfo where code = :code and date = :date",
                                {"code": code, "date": date})
    if data is None:
        return None
    dto = PriceInfo(code=data[0], date=data[1], price=data[2], pe=data[3], pb=data[4])
    return dto

def priceinfo_from_api(code, date):
    rs = bs.query_history_k_data_plus(code,
                                      "date,code,close,peTTM,pbMRQ",
                                      start_date=date,
                                      end_date=date,
                                      frequency="d",
                                      adjustflag="3")
    result = None
    if rs.error_code != '0':
        print(code, rs.error_code, rs.error_msg)
    if rs.next():
        item = rs.get_row_data()
        result = PriceInfo(code=item[1], date=item[0], price=float(item[2]),
                           pe=float(item[3]), pb=float(item[4]))
        sqliteTool = SqliteTool()
        sqliteTool.operate_one('insert or replace into priceinfo values(?,?,?,?,?) ',
                               (result.code, result.date, result.price, result.pe, result.pb))
    return result



def listPrice():
    sqliteTool = SqliteTool()
    datas = sqliteTool.query_many("select * from priceinfo where pe > 5 and pe < 20")
    result = []
    for data in datas:
        dto = PriceInfo(code=data[0], date=data[1], price=data[2], pe=data[3], pb=data[4])
        result.append(dto)
    return result


if __name__ == "__main__":
    # 创建数据表info的SQL语句
    # create_tb_sql = ("create table if not exists priceinfo ("
    #                  "code text primary key,"
    #                  "date text,"
    #                  "price float default 0,"
    #                  "pe float default 0,"
    #                  "pb float default 0"
    #                  ");")
    # # 创建对象
    # sqliteTool = SqliteTool()
    # # 创建数据表
    # sqliteTool.drop_table("drop table priceinfo;")
    # sqliteTool.create_table(create_tb_sql)
    #
    # from allstock import allstock
    #
    # stocks = allstock()
    # bs.login()
    # date = '2024-04-26'
    # for stock in stocks:
    #     rs = bs.query_history_k_data_plus(stock.code,
    #                                       "date,code,close,peTTM,pbMRQ",
    #                                       start_date=date,
    #                                       end_date=date,
    #                                       frequency="d",
    #                                       adjustflag="3")
    #     if rs.error_code != '0':
    #         print(stock.code, stock.name, rs.error_code, rs.error_msg)
    #         continue
    #     if rs.next():
    #         item = rs.get_row_data()
    #         print(item)
    #         sqliteTool.operate_one('insert or replace into priceinfo values(?,?,?,?,?) ',
    #                                (item[1], item[0], item[2], item[3], item[4]))
    # bs.logout()

    data = priceinfo('sh.601939', "2024-05-08")
    print(data)
