import pandas as pd
from datetime import datetime


def extract_table_from_excel(file_path):
    xl = pd.ExcelFile(file_path)
    tables_content = []
    for sheet_name in xl.sheet_names:
        df = xl.parse(sheet_name)
        df_converted = df.applymap(convert_timestamp)
        tables_content.append(df_converted.values.tolist())
    return tables_content


def convert_timestamp(item):
    if isinstance(item, datetime):
        return item.isoformat()
    return item
