from collections import namedtuple

import akshare as ak

from stocks.SqliteTool import SqliteTool

# 同花顺-分红配送

HsFhps = namedtuple("HsFhps",
                    [
                        "code",
                        "报告期",
                        "董事会日期",
                        "股东大会预案公告日期",
                        "实施公告日",
                        "分红方案说明",
                        "A股股权登记日",
                        "A股除权除息日",
                        "分红总额",
                        "方案进度",
                        "股利支付率",
                        "税前分红率",
                    ])


class HsFhpsRepository:

    def __init__(self, db_path: str):
        self.db_path = db_path

    def create_table(self):
        # %s#\s\+\(.*\)\s\(.*\)\s,#"\1" \2,#
        sql = """
        create table if not exists hs_fhps(
        code text,
        "报告期" string,
        "董事会日期" string,
        "股东大会预案公告日期" string,
        "实施公告日" string,
        "分红方案说明" string,
        "A股股权登记日" string,
        "A股除权除息日" string,
        "分红总额" string,
        "方案进度" string,
        "股利支付率" string,
        "税前分红率" string
        ); 
        """
        sqlite_tool = SqliteTool(self.db_path)
        # 创建数据表
        sqlite_tool.drop_table("drop table hs_fhps;")
        sqlite_tool.create_table(sql)
        sqlite_tool.close_con()

    def fetch_from_api(self, code: str):
        df = ak.stock_fhps_detail_ths(symbol=code)
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
        print(item.报告期, item.分红总额, item.股利支付率, item.税前分红率)
