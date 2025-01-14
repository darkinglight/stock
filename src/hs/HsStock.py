from stocks.SqliteTool import SqliteTool
import akshare as ak


class HsStockRepository:

    def __init__(self, db_path: str = "finance.db"):
        self.db_path = db_path

    def init_table(self):
        # 创建数据表info的SQL语句
        create_tb_sql = ("create table if not exists hs_stock("
                         "code text primary key,"
                         "name text"
                         ");")
        sqlite_tool = SqliteTool(self.db_path)
        # 创建数据表
        sqlite_tool.create_table(create_tb_sql)
        sqlite_tool.close_con()

    def drop_table(self):
        sqlite_tool = SqliteTool(self.db_path)
        sqlite_tool.drop_table("drop table hs_stock;")
        sqlite_tool.close_con()

    def init_hs_stock(self):
        # 获取数据
        df = ak.stock_info_a_code_name()
        sql = 'insert into hs_stock values(?,?)'
        sqlite_tool = SqliteTool(self.db_path)
        sqlite_tool.operate_many(sql, [tuple(row) for index, row in df.iterrows()])
        sqlite_tool.close_con()


if __name__ == "__main__":
    repository = HsStockRepository()
    repository.init_table()
    repository.init_hs_stock()
