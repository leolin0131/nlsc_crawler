import pandas as pd

df = pd.DataFrame({
    '縣市': ['桃園市', '桃園市'],
    '鄉鎮市區': ['中壢區', '平鎮區'],
    '地段': ['0204', 1236],
    '地段.1': ['三座屋段三座屋小段', '平德段'],
    '地號': ['1345-84', 1],
    '公告現值': [None, None]
})

sect_col = None
for col in df.columns:
    if '地段' in str(col):
        sample = str(df[col].dropna().iloc[0])
        print(f"Col {col}, first sample: '{sample}', isdigit(): {sample.isdigit()}")
        if sample.isdigit():
            sect_col = col
            break
            
print("sect_col:", sect_col)
