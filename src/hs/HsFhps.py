import datetime
from collections import namedtuple

import akshare as ak

from hs.HsDetail import HsDetailRepository
from stocks.SqliteTool import SqliteTool

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
            "最新公告日期" datetime,
            update_at text -- 最后更新日期
        ); 
        """
        sqlite_tool = SqliteTool(self.db_path)
        # 创建数据表
        sqlite_tool.create_table(sql)
        sqlite_tool.close_con()

    def drop_table(self):
        sqlite_tool = SqliteTool(self.db_path)
        sqlite_tool.drop_table("drop table hs_fhps;")
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
            if entity[3] == 0:
                continue
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

    def get_latest_update_time(self, code: str):
        # 查询最新的更新时间
        sqlite_tool = SqliteTool(self.db_path)
        row = sqlite_tool.query_one(f"select max(update_at) from hs_fhps where code = '{code}'")
        sqlite_tool.close_con()
        if row[0]:
            return datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
        else:
            return datetime.datetime.min

    def refresh(self, code: str):
        latest_update_time = self.get_latest_update_time(code)
        # 计算时间差
        time_diff = datetime.datetime.now() - latest_update_time
        if time_diff.total_seconds() > 3600 * 24 * 7:
            try:
                rows = self.__fetch_from_api(code)
                rows = rows[rows['方案进度'] == '实施分配']
                rows.fillna(0, inplace=True)
                rows['update_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # 根据字典的键动态生成插入语句
                sql = ('INSERT INTO hs_fhps ("code", "' + '", "'.join(rows.columns.values) + '") VALUES (?, ' +
                       ', '.join(['?'] * rows.shape[1]) + ')')
                # 执行批量插入操作
                sqlite_tool = SqliteTool(self.db_path)
                sqlite_tool.delete_record(f"delete from hs_fhps where code = '{code}'")
                sqlite_tool.operate_many(sql, [(code,) + tuple(row) for index, row in rows.iterrows()])
                sqlite_tool.close_con()
                hs_detail_repository = HsDetailRepository(self.db_path)
                hs_detail_repository.update_bonus(code, self.__get_bonus_rate(code))
            except TypeError:
                hs_detail_repository = HsDetailRepository(self.db_path)
                hs_detail_repository.update_bonus(code, 0)


    def refresh_all(self):
        hs_detail_repository = HsDetailRepository(self.db_path)
        hs_details = hs_detail_repository.fetch_all_from_db()
        for hs_detail in hs_details:
            try:
                self.refresh(hs_detail.code)
            except Exception as e:
                print(f"refresh {hs_detail.code} failed, {e}")
                raise e


    def get_bonus_rate(self, code: str) -> float:
        if self.data.get(code) is None:
            try:
                self.refresh(code)
                self.data[code] = self.__get_bonus_rate(code)
            except TypeError:
                self.data[code] = 0
        return self.data[code]


if __name__ == "__main__":
    repository = HsFhpsRepository("finance.db")
    repository.drop_table()
    repository.init_table()
    repository.refresh("002931")
    # for item in repository.list_from_db("002867"):
    #     print(item.报告期, item.每股净资产, item.每股收益, item.现金分红现金分红比例, item.现金分红股息率)
    print(repository.get_bonus_rate("002931"))
