import toga

from stocks import hkstock


def stock_list():
    hkstock.init_table()
    rows = hkstock.fetch_all_from_db()
    # print(rows)
    # data = [("root%s" % i, "value %s" % i) for i in range(1, 100)]
    data = [(row.code, row.name) for row in rows]
    return toga.Table(headings=["code", "name"], data=data)