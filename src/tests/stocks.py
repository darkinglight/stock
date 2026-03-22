import akshare as ak

stock_financial_abstract_new_ths_df = ak.stock_financial_abstract_new_ths(symbol="000063", indicator="按报告期")
# 循环输出所有内容到txt文件
with open("stock_data_output.txt", "w", encoding="utf-8") as f:
    f.write("DataFrame 列名:\n")
    f.write(str(list(stock_financial_abstract_new_ths_df.columns)) + "\n")
    f.write("\nDataFrame 数据:\n")
    for index, row in stock_financial_abstract_new_ths_df.iterrows():
        f.write(f"\n第 {index} 行:\n")
        for col in stock_financial_abstract_new_ths_df.columns:
            f.write(f"{col}: {row[col]}\n")
print("数据已成功输出到 stock_data_output.txt 文件")