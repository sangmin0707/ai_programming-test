import pandas as pd
df = pd.read_csv("scores_2026.csv")
print(df['점수'].mean())

df = pd.read_csv("scores_2026.csv")
df.shape             
df["점수"].isna().sum() 
df.duplicated().sum() 
df["반"].unique()          
df["과목"].unique()    
df["점수"].describe()