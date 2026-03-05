import pandas as pd
import sys

# 讀取最新的 Excel 檔案
file_path = 'uploads/temp_1770969341001_202602_FND_ERP工作報告.xlsx'

try:
    # 讀取 Excel，不指定 header
    df_raw = pd.read_excel(file_path, header=None)
    print("=" * 60)
    print("原始資料前 20 行：")
    print("=" * 60)
    print(df_raw.head(20))
    
    # 尋找標題行
    target_col = "填單人員"
    header_row_idx = -1
    
    for idx, row in df_raw.head(20).iterrows():
        row_values = [str(x).strip() for x in row.values]
        if target_col in row_values:
            header_row_idx = idx
            print(f"\n找到標題行在索引 {idx}")
            break
    
    if header_row_idx == -1:
        print("\n未找到標題行，使用第 0 行")
        header_row_idx = 0
    
    # 重新讀取，設定 header
    df = pd.read_excel(file_path, header=header_row_idx)
    df.columns = df.columns.astype(str).str.strip()
    
    print("\n" + "=" * 60)
    print("欄位名稱：")
    print("=" * 60)
    print(df.columns.tolist())
    
    if target_col in df.columns:
        # Forward fill 合併儲存格
        df[target_col] = df[target_col].ffill()
        
        # 移除空值
        df_clean = df.dropna(subset=[target_col])
        
        # 清理字串
        df_clean[target_col] = df_clean[target_col].astype(str).str.strip()
        
        # 取得唯一值
        users = df_clean[target_col].unique().tolist()
        users = [str(u).strip() for u in users if str(u).strip() and str(u) != 'nan']
        
        print("\n" + "=" * 60)
        print("填單人員欄位的唯一值（經過 ffill 和清理後）：")
        print("=" * 60)
        for i, user in enumerate(users, 1):
            print(f"{i}. {user}")
        
        print("\n" + "=" * 60)
        print(f"總共人員數量: {len(users)}")
        print("=" * 60)
        
        # 顯示每個人員的資料筆數
        print("\n每個人員的資料筆數：")
        for user in users:
            count = len(df_clean[df_clean[target_col] == user])
            print(f"  {user}: {count} 筆")
            
    else:
        print(f"\n錯誤：找不到 '{target_col}' 欄位")
        
except Exception as e:
    print(f"錯誤: {e}")
    import traceback
    traceback.print_exc()
