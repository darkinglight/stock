from collections import namedtuple

import akshare as ak

from stocks.SqliteTool import SqliteTool

# todo 更新财报后自动更新
HsFhps = namedtuple("HsFhps",
                    [
                        "code",
                        "bonus_rate",  # 分红率
                    ])


class HsFhpsRepository:

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.data = {}
        entities = self.__list_bonus_rate()
        for entity in entities:
            self.data[entity.code] = entity.bonus_rate

    def init_table(self):
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
        sqlite_tool.create_table(sql)
        sqlite_tool.close_con()

    def __fetch_from_api(self, code: str):
        df = ak.stock_fhps_detail_em(symbol=code)
        return df

    # 最近平均分红率
    def __get_bonus_rate(self, code: str) -> float:
        sql = f"""
        SELECT 
            code, 
            substr(报告期, 1, 4) as year, 
            sum("现金分红-现金分红比例" / 10) as bonus, 
            max(每股收益) as eps
        FROM
            hs_fhps
        WHERE
            报告期 > "2020-12-31" and code = '{code}'
        GROUP BY
            code, year
        """
        sqlite_tool = SqliteTool(self.db_path)
        rows = sqlite_tool.query_many(sql)
        sqlite_tool.close_con()
        result = []
        for entity in rows:
            result.append(entity[2] / entity[3])
        return round(sum(result) / len(result), 2) if len(result) > 0 else 0

    def __list_bonus_rate(self) -> list[HsFhps]:
        sql = """
        SELECT 
            code, 
            round(sum(bonus) / sum(eps), 2) 
        FROM (
            SELECT 
                code, 
                substr(报告期, 1, 4) as year, 
                sum("现金分红-现金分红比例" / 10) as bonus, 
                max(每股收益) as eps
            FROM 
                hs_fhps
            WHERE 
                报告期 > "2020-12-31"
            GROUP BY 
                code, year
        ) GROUP BY
            code
        """
        sqlite_tool = SqliteTool(self.db_path)
        rows = sqlite_tool.query_many(sql)
        sqlite_tool.close_con()
        if not rows:
            return []
        return [HsFhps(*row) for row in rows]

    def __delete(self, code: str):
        sqlite_tool = SqliteTool(self.db_path)
        sqlite_tool.delete_record(f"delete from hs_fhps where code = '{code}'")
        sqlite_tool.close_con()

    def __refresh(self, code: str):
        rows = self.__fetch_from_api(code)
        rows.fillna("", inplace=True)
        # 根据字典的键动态生成插入语句
        sql = ('INSERT INTO hs_fhps ("code", "' + '", "'.join(rows.columns.values) + '") VALUES (?, ' +
               ', '.join(['?'] * rows.shape[1]) + ')')
        # 删除历史记录
        self.__delete(code)
        # 执行批量插入操作
        sqlite_tool = SqliteTool(self.db_path)
        sqlite_tool.operate_many(sql, [(code,) + tuple(row) for index, row in rows.iterrows()])
        sqlite_tool.close_con()

    def get_bonus_rate(self, code: str) -> float:
        if self.data.get(code) is None:
            self.__refresh(code)
            self.data[code] = self.__get_bonus_rate(code)
        return self.data[code]


if __name__ == "__main__":
    repository = HsFhpsRepository("finance.db")
    # repository.create_table()
    # repository.refresh("002867")
    # for item in repository.list_from_db("002867"):
    #     print(item.报告期, item.每股净资产, item.每股收益, item.现金分红现金分红比例, item.现金分红股息率)
    print(repository.get_bonus_rate("002884"))
