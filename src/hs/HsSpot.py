import datetime
from collections import namedtuple

from hs.HsDetail import HsDetailRepository
from stocks.SqliteTool import SqliteTool
import akshare as ak

HsSpot = namedtuple("HsSpot", [
    "code",
    "name",
    "pe",
    "pb",
])


class HsSpotRepository:

    def __init__(self, db_path: str = "finance.db"):
        self.db_path = db_path

    def init_table(self):
        # %s#\s\+\(.*\)\s\(.*\)\s,#"\1" \2,#
        sql = """
        create table if not exists hs_spot(
            "序号" int64,
            "代码" text primary key,
            "名称" text,
            "最新价" float64,
            "涨跌幅" float64, -- 注意单位:%
            "涨跌额" float64,
            "成交量" float64, -- 注意单位:手
            "成交额" float64, -- 注意单位:元
            "振幅" float64, -- 注意单位:%
            "最高" float64,
            "最低" float64,
            "今开" float64,
            "昨收" float64,
            "量比" float64,
            "换手率" float64, -- 注意单位:%
            "市盈率-动态" float64,
            "市净率" float64,
            "总市值" float64, -- 注意单位:元
            "流通市值" float64, -- 注意单位:元
            "涨速" float64,
            "5分钟涨跌" float64, -- 注意单位:%
            "60日涨跌幅" float64, -- 注意单位:%
            "年初至今涨跌幅" float64, -- 注意单位:%
            update_at text -- 更新时间
        ); 
        """
        sqlite_tool = SqliteTool(self.db_path)
        # 创建数据表
        sqlite_tool.create_table(sql)
        sqlite_tool.close_con()

    def drop_table(self):
        sqlite_tool = SqliteTool(self.db_path)
        sqlite_tool.drop_table("drop table hs_spot;")
        sqlite_tool.close_con()

    def get_latest_update_time(self):
        # 查询最新的更新时间
        sqlite_tool = SqliteTool(self.db_path)
        row = sqlite_tool.query_one("select max(update_at) from hs_spot")
        sqlite_tool.close_con()
        if row[0]:
            return datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
        else:
            return datetime.datetime.min

    def refresh(self):
        # 1. 无记录,时间为min < 当天15:00 2.更新日期 < 当天15:00
        latest_update_time = self.get_latest_update_time()
        # 计算时间差
        time_diff = datetime.datetime.now() - latest_update_time
        # 计算当天 15:00 的时间
        today_1500 = datetime.datetime.now().replace(hour=15, minute=00, second=0, microsecond=0)
        if latest_update_time < today_1500 and time_diff.total_seconds() > 3600:
            # 获取数据
            rows = ak.stock_zh_a_spot_em()
            rows = rows[rows['市净率'] > 0]
            rows['update_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # 根据字典的键动态生成插入语句
            sql = ('INSERT INTO hs_spot ("' + '", "'.join(rows.columns.values) + '") VALUES (' +
                   ', '.join(['?'] * rows.shape[1]) + ')')
            sqlite_tool = SqliteTool(self.db_path)
            sqlite_tool.delete_record("delete from hs_spot")
            sqlite_tool.operate_many(sql, [tuple(row) for index, row in rows.iterrows()])
            sqlite_tool.close_con()
            hs_detail_repository = HsDetailRepository(self.db_path)
            for index, row in rows.iterrows():
                hs_detail_repository.upsert_price(row["代码"], row["名称"], row["市盈率-动态"], row["市净率"])

    def fetch_one_from_db(self, code: str):
        sqlite_tool = SqliteTool(self.db_path)
        row = sqlite_tool.query_one(f'select 代码, 名称, "市盈率-动态", 市净率 from hs_spot where 代码 = "{code}"')
        sqlite_tool.close_con()
        return HsSpot(*row)

    def fetch_all_from_db(self) -> list[HsSpot]:
        sqlite_tool = SqliteTool(self.db_path)
        rows = sqlite_tool.query_many('select 代码, 名称, "市盈率-动态", 市净率 from hs_spot where 市净率 is not Null')
        sqlite_tool.close_con()
        if rows is None:
            return []
        return [HsSpot(*item) for item in rows]

    def list_low_price_10(self) -> list[HsSpot]:
        sql = """
        SELECT 
            代码, 
            名称, 
            "市盈率-动态", 
            市净率
        FROM
            hs_spot 
        WHERE
            0 < 市净率 AND 市净率 < 2 AND "市盈率-动态" > 0 AND "市盈率-动态" < 15
        ORDER BY
            "市盈率-动态"
        LIMIT 10
        """
        sqlite_tool = SqliteTool(self.db_path)
        rows = sqlite_tool.query_many(sql)
        sqlite_tool.close_con()
        if rows is None:
            return []
        return [HsSpot(*item) for item in rows]


if __name__ == "__main__":
    repository = HsSpotRepository()
    repository.init_table()
    repository.refresh()
    # for row in repository.fetch_all_from_db():
    #     print(row.code, row.name)
    print(repository.fetch_all_from_db())
