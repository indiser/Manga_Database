import pandas as pd

df = pd.read_csv('manga_all.csv')
df.to_parquet('manga_all.parquet', engine='pyarrow', compression='snappy')
