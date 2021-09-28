"""import sqlite3
import pandas as pd
import pathlib as Path
from pathlib import Path
file_path = Path(__file__).parent.absolute()
conn = sqlite3.connect(file_path.joinpath("variable_history.sqlite3"))

previous_data = pd.read_sql_query(f"SELECT SourceTimestamp, Value FROM '2_10016' where SourceTimestamp >=datetime('now', '-1 Hour')", conn)

print(previous_data)"""
"""from datetime import datetime, timedelta

current_hour = datetime.now().replace(microsecond=0, second=0,minute=0)-timedelta(hours=10)
print(current_hour.hour)"""

test=[i for i in range(1,61)]
print(test)
print(len(test))