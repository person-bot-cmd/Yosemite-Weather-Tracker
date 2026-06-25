import pandas as pd
df = pd.read_csv("daily_log.csv", skipinitialspace=True)
print(df.columns.tolist())
print(df.head())
