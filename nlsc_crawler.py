import pandas as pd
import requests
import urllib3
import time
import random
import argparse
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 縣市代碼對照表
CITY_MAP = {
    '臺北市': 'A', '台北市': 'A',
    '臺中市': 'B', '台中市': 'B',
    '基隆市': 'C',
    '臺南市': 'D', '台南市': 'D',
    '高雄市': 'E',
    '新北市': 'F',
    '宜蘭縣': 'G',
    '桃園市': 'H', '桃園縣': 'H',
    '嘉義市': 'I',
    '新竹縣': 'J',
    '苗栗縣': 'K',
    '南投縣': 'M',
    '彰化縣': 'N',
    '新竹市': 'O',
    '雲林縣': 'P',
    '嘉義縣': 'Q',
    '屏東縣': 'T',
    '花蓮縣': 'U',
    '臺東縣': 'V', '台東縣': 'V',
    '金門縣': 'W',
    '澎湖縣': 'X',
    '連江縣': 'Z'
}

# 權利人類別對照表
LCDETYPENAME = {
    "lcde_1": "本國人",
    "lcde_2": "外國人",
    "lcde_3": "國有",
    "lcde_4": "省市",
    "lcde_5": "縣市",
    "lcde_6": "鄉鎮市",
    "lcde_7": "本國私法人",
    "lcde_8": "外國法人",
    "lcde_9": "祭祀公業",
    "lcde_a": "其他",
    "lcde_b": "銀行法人",
    "lcde_c": "大陸地區自然人",
    "lcde_d": "大陸地區法人"
}

def pad_land_no(landno):
    """將地號轉換為8碼格式，例如 '1' -> '00010000', '1345-84' -> '13450084'"""
    parts = str(landno).strip().split('-')
    if len(parts) == 1:
        return parts[0].zfill(4) + "0000"
    else:
        return parts[0].zfill(4) + parts[1].zfill(4)

def parse_owner(lcdetype):
    """解析權利人類別"""
    if not isinstance(lcdetype, dict):
        return ""
    
    owners = []
    # 處理特殊 lcde_1 (本國人) 的細項 (lcde_1_m, lcde_1_f 等可能加總)
    s1 = 0.0
    for k, v in lcdetype.items():
        if "lcde_1" in k and isinstance(v, (int, float)):
            s1 += float(v)
    
    if s1 > 0:
        ratio = min(s1 * 100, 100)
        owners.append(f"本國人:{ratio:.2f}%".replace(".00%", "%"))
        
    for k, v in lcdetype.items():
        if k.startswith("lcde_") and "lcde_1" not in k:
            if isinstance(v, (int, float)) and v > 0:
                ratio = min(v * 100, 100)
                name = LCDETYPENAME.get(k, k)
                owners.append(f"{name}:{ratio:.2f}%".replace(".00%", "%"))
                
    return " / ".join(owners)

def get_land_info(city_code, sect_code, landno):
    session = requests.Session()
    session.verify = False
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://maps.nlsc.gov.tw',
        'Referer': 'https://maps.nlsc.gov.tw/T09/mobilemap.action'
    }
    
    url = "https://api.nlsc.gov.tw/S09_Ralid/getLandInfoSect"
    data = {
        'city': city_code,
        'sect': str(sect_code).strip().zfill(4),
        'landno': pad_land_no(landno)
    }
    
    try:
        res = session.post(url, headers=headers, data=data, timeout=10)
        if res.status_code == 200:
            json_data = res.json()
            if not json_data:
                return None, None
            
            # 公告現值
            val = None
            if 'ralid' in json_data and isinstance(json_data['ralid'], dict):
                val = json_data['ralid'].get('AA16')
                
            # 所有權人類別
            owner = ""
            if 'lcdetype' in json_data:
                owner = parse_owner(json_data['lcdetype'])
                
            return val, owner
    except Exception as e:
        print(f"Error fetching data for {city_code}-{sect_code}-{landno}: {e}")
    return None, None

def is_public_type(name):
    """判斷是否為公有/國有相關類別（國有、省市、縣市、鄉鎮市，或包含 XX鄉、XX鎮、XX市）"""
    name = str(name).strip()
    if not name:
        return False
    if name in {'國有', '省市', '縣市', '鄉鎮市', '中華民國'}:
        return True
    if '國有' in name or '公所' in name or '政府' in name:
        return True
    # 包含 XX鄉、XX鎮、XX市，且排除自然人/私法人相關字樣
    if any(k in name for k in ['鄉', '鎮', '市']):
        if not any(ex in name for ex in ['人', '法人', '祭祀公業', '其他']):
            return True
    return False

def is_private_type(name):
    """判斷是否為私有相關類別（自然人、私法人、祭祀公業等）"""
    name = str(name).strip()
    if not name:
        return False
    return not is_public_type(name)

def categorize_ownership(owner_str):
    if not owner_str:
        return ""
    
    owner_str = str(owner_str)
    
    # 用 / 分割，並取出冒號前面的名稱
    parts = [p.split(':')[0].strip() for p in owner_str.split('/') if ':' in p]
    if not parts:
        # 應對如果沒有冒號的情況
        parts = [p.strip() for p in owner_str.split('/') if p.strip()]
        
    if not parts:
        return ""
        
    types_set = set(parts)
    
    has_public = any(is_public_type(t) for t in types_set)
    has_private = any(is_private_type(t) for t in types_set)
    
    # 1. 全部為公有/國有/鄉鎮市/省市/縣市 (例如 國有:100%, 鄉鎮市:100%, 國有:20% / 鄉鎮市:80%)
    if has_public and not has_private:
        return '國有'
        
    # 2. 同時包含公有與私有 (例如 本國人:40% / 鄉鎮市:60%, 本國人:50% / 國有:50%)
    if has_public and has_private:
        return '公私共有'
        
    # 3. 只有本國人
    if types_set == {'本國人'}:
        return '私有'
        
    # 4. 只有本國私法人
    if types_set == {'本國私法人'}:
        return '本國私法人'
        
    return ""

def process_file(input_file, output_file):
    print(f"讀取檔案: {input_file}")
    
    # 自動判斷副檔名
    ext = os.path.splitext(input_file)[1].lower()
    if ext == '.csv':
        df = pd.read_csv(input_file)
    elif ext in ['.xls', '.xlsx']:
        df = pd.read_excel(input_file)
    else:
        raise ValueError("不支援的檔案格式，請提供 CSV 或 Excel 檔案")

    # 尋找必要的欄位
    # 假設欄位名稱包含「縣市」、「地段」跟「地號」
    city_col = next((col for col in df.columns if '縣市' in col), None)
    
    # 找地段代碼 (通常是純數字，而且在截圖中是在欄位C)
    sect_col = None
    for col in df.columns:
        if '地段' in str(col):
            # 檢查前10筆資料是否有純數字(代碼)
            has_digit = False
            for val in df[col].dropna().head(10):
                val_str = str(val).strip()
                # 處理浮點數 (如 1236.0) 或純數字字串
                if val_str.replace('.', '', 1).isdigit():
                    has_digit = True
                    break
            if has_digit:
                sect_col = col
                break
                
    # Fallback: 如果還是找不到，但有包含「地段」的欄位，就直接選第一個
    if not sect_col:
        for col in df.columns:
            if '地段' in str(col):
                sect_col = col
                break
    
    landno_col = next((col for col in df.columns if '地號' in col), None)

    if not city_col or not sect_col or not landno_col:
        print("找不到必要的欄位，請確認檔案中有包含「縣市」、代表代碼的「地段」、以及「地號」欄位")
        print("目前欄位：", list(df.columns))
        return

    print(f"識別出欄位 - 縣市: {city_col}, 地段代碼: {sect_col}, 地號: {landno_col}")
    
    # 準備新欄位並強制轉為字串型別，避免 pandas 型別錯誤
    if '公告現值' not in df.columns:
        df['公告現值'] = ""
    df['公告現值'] = df['公告現值'].fillna("").astype(str)
    
    if '權利人類別' not in df.columns:
        df['權利人類別'] = ""
    df['權利人類別'] = df['權利人類別'].fillna("").astype(str)
    
    if '土地類別' not in df.columns:
        df['土地類別'] = ""
    df['土地類別'] = df['土地類別'].fillna("").astype(str)
        
    total_rows = len(df)
    for index, row in df.iterrows():
        city_name = str(row[city_col]).strip()
        
        # 處理 sect_code，可能被 pandas 讀成浮點數 (1236.0)
        raw_sect = str(row[sect_col]).strip()
        if raw_sect.replace('.', '', 1).isdigit() and '.' in raw_sect:
            raw_sect = str(int(float(raw_sect)))
        sect_code = raw_sect
        
        landno = str(row[landno_col]).strip()
        
        city_code = CITY_MAP.get(city_name)
        if not city_code:
            print(f"[{index+1}/{total_rows}] 錯誤: 找不到縣市 {city_name} 的代碼")
            continue
            
        print(f"[{index+1}/{total_rows}] 查詢 {city_name} {sect_code} {landno} ...", end=" ")
        
        val, owner = get_land_info(city_code, sect_code, landno)
        if val is not None or owner:
            df.at[index, '公告現值'] = str(val) if val is not None else ""
            df.at[index, '權利人類別'] = str(owner)
            df.at[index, '土地類別'] = categorize_ownership(owner)
            print(f"OK (現值: {val}, 權利人: {owner}, 土地類別: {df.at[index, '土地類別']})")
        else:
            print("查無資料")
            
        # 每查詢 50 筆休息 20 秒，其餘隨機間隔 1.5 ~ 3 秒
        if (index + 1) % 50 == 0 and (index + 1) < total_rows:
            print("  >> 已查詢 50 筆，冷卻休息 20 秒...")
            time.sleep(20)
        else:
            time.sleep(random.uniform(1.5, 3.0))
        
    print(f"儲存結果至: {output_file}")
    if ext == '.csv':
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
    else:
        df.to_excel(output_file, index=False)
    print("完成！")

if __name__ == "__main__":
    import sys
    
    # 支援直接拖曳檔案或雙擊執行
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
    else:
        print("國土測繪雲公告現值與所有權人爬蟲工具")
        input_file = input("請輸入或將 Excel/CSV 檔案拖曳至此視窗，然後按 Enter: ").strip(' "\'')
        output_file = None
        
    if not input_file or not os.path.exists(input_file):
        print(f"錯誤：找不到檔案 {input_file}")
    else:
        if not output_file:
            base, ext = os.path.splitext(input_file)
            output_file = f"{base}_result{ext}"
            
        try:
            process_file(input_file, output_file)
        except Exception as e:
            print(f"發生未預期的錯誤: {e}")
            
    input("\n處理完畢，請按 Enter 鍵結束視窗...")
