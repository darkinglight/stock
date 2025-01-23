from collections import namedtuple

import akshare as ak

from stocks.SqliteTool import SqliteTool

HsFhps = namedtuple("HsFhps",
                    [
                        "code",
                        "date",
                        "bonus",  # 每股分红
                        "eps",  # 每股盈利
                        "bonus_rate",  # 分红率
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

    def fetch_from_db(self, code: str, date: str) -> HsFhps:
        sqlite_tool = SqliteTool(self.db_path)
        row = sqlite_tool.query_one(
            'select code, 报告期, "现金分红-现金分红比例", 每股收益 from hs_fhps where code = ? and "报告期" = ?',
            (code, date))
        sqlite_tool.close_con()
        return HsFhps(*row)

    def list_from_db(self, code: str) -> list[HsFhps]:
        sqlite_tool = SqliteTool(self.db_path)
        rows = sqlite_tool.query_many(
            'select code, 报告期, "现金分红-现金分红比例", 每股收益 from hs_fhps where code = ?',
            (code,))
        sqlite_tool.close_con()
        if not rows:
            return []
        return [HsFhps(*row, None) for row in rows]

    # 最近平均分红率
    def get_bonus_rate(self, code: str) -> float:
        entities = self.list_from_db(code)
        result = []
        for entity in entities:
            if entity.date > '2020-01-01':
                result.append(entity.bonus_per_stock / entity.eps / 10)
        return sum(result) / len(result)

    def list_bonus_rate(self) -> list[HsFhps]:
        sql = 'select code, 报告期, sum("现金分红-现金分红比例" / 10), max(每股收益) from hs_fhps group by code, 报告期'
        sqlite_tool = SqliteTool(self.db_path)
        rows = sqlite_tool.query_many(sql)
        sqlite_tool.close_con()
        if not rows:
            return []
        return [HsFhps(*row, row[2] / row[3]) for row in rows]

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
    # repository.create_table()
    # repository.refresh("002867")
    # for item in repository.list_from_db("002867"):
    #     print(item.报告期, item.每股净资产, item.每股收益, item.现金分红现金分红比例, item.现金分红股息率)
    # print(repository.get_bonus_rate("002867"))
    print(repository.list_bonus_rate())
