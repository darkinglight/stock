from collections import namedtuple

import akshare as ak

from stocks.SqliteTool import SqliteTool

HsFhps = namedtuple("HsFhps",
                    [
                        "code",
                        "报告期",
                        "业绩披露日期",
                        "送转股份送转总比例",
                        "送转股份送股比例",
                        "送转股份转股比例",
                        "现金分红现金分红比例",
                        "现金分红现金分红比例描述",
                        "现金分红股息率",
                        "每股收益",
                        "每股净资产",
                        "每股公积金",
                        "每股未分配利润",
                        "净利润同比增长",
                        "总股本",
                        "预案公告日",
                        "股权登记日",
                        "除权除息日",
                        "方案进度",
                        "最新公告日期",
                    ])


class HsFhpsRepository:

    def __init__(self, db_path: str):
        self.db_path = db_path

    def create_table(self):
        # %s#\s\+\(.*\)\s\(.*\)\s,#"\1" \2,#
        sql = """
        create table if not exists hs_fhps(
        code text,
        "报告期" datetime,
        "业绩披露日期" datetime,
        "送转股份-送转总比例" float64,
        "送转股份-送股比例" float64,
        "送转股份-转股比例" float64,
        "现金分红-现金分红比例" float64,
        "现金分红-现金分红比例描述" text,
        "现金分红-股息率" float64,
        "每股收益" float64,
        "每股净资产" float64,
        "每股公积金" float64,
        "每股未分配利润" float64,
        "净利润同比增长" float64,
        "总股本" int64,
        "预案公告日" datetime,
        "股权登记日" datetime,
        "除权除息日" datetime,
        "方案进度" text,
        "最新公告日期" datetime
        ); 
        """
        sqlite_tool = SqliteTool(self.db_path)
        # 创建数据表
        sqlite_tool.drop_table("drop table hs_fhps;")
        sqlite_tool.create_table(sql)
        sqlite_tool.close_con()

    def fetch_from_api(self, code: str):
        df = ak.stock_fhps_detail_em(symbol=code)
        return df

    def fetch_from_db(self, code: str, date: str):
        sqlite_tool = SqliteTool(self.db_path)
        row = sqlite_tool.query_one('select * from hs_fhps where code = ? and "报告期" = ?',
                                    (code, date))
        sqlite_tool.close_con()
        return HsFhps(*row)

    def list_from_db(self, code: str):
        sqlite_tool = SqliteTool(self.db_path)
        rows = sqlite_tool.query_many('select * from hs_fhps where code = ?',
                                      (code,))
        sqlite_tool.close_con()
        if not rows:
            return []
        return [HsFhps(*row) for row in rows]

    def get_bonus_rate(self, code: str):
        entities = self.list_from_db(code)
        # sum(每年分红) /

    def delete(self, code: str):
        sqlite_tool = SqliteTool(self.db_path)
        sqlite_tool.delete_record(f"delete from hs_fhps where code = '{code}'")
        sqlite_tool.close_con()

    def refresh(self, code: str):
        rows = self.fetch_from_api(code)
        rows.fillna("", inplace=True)
        # 根据字典的键动态生成插入语句
        sql = ('INSERT INTO hs_fhps ("code", "' + '", "'.join(rows.columns.values) + '") VALUES (?, ' +
               ', '.join(['?'] * rows.shape[1]) + ')')
        # 删除历史记录
        self.delete(code)
        # 执行批量插入操作
        sqlite_tool = SqliteTool(self.db_path)
        sqlite_tool.operate_many(sql, [(code,) + tuple(row) for index, row in rows.iterrows()])
        sqlite_tool.close_con()

    def refresh_all(self, codes: tuple):
        for code in codes:
            self.refresh(code)
            print(code, "finish")


if __name__ == "__main__":
    repository = HsFhpsRepository("finance.db")
    repository.create_table()
    repository.refresh("002867")
    for item in repository.list_from_db("002867"):
        print(item.报告期, item.每股净资产, item.每股收益, item.现金分红现金分红比例, item.现金分红股息率)
