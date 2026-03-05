import pandas as pd

# 讀取最新的 Excel 檔案
file_path = 'uploads/temp_1770969341001_202602_FND_ERP工作報告.xlsx'

try:
    # 讀取 Excel
    df_raw = pd.read_excel(file_path, header=None)
    
    # 尋找標題行
    target_col = "填單人員"
    header_row_idx = -1
    
    for idx, row in df_raw.head(20).iterrows():
        row_values = [str(x).strip() for x in row.values]
        if target_col in row_values:
            header_row_idx = idx
            break
    
    if header_row_idx == -1:
        header_row_idx = 0
    
    # 重新讀取
    df = pd.read_excel(file_path, header=header_row_idx)
    df.columns = df.columns.astype(str).str.strip()
    
    if target_col in df.columns:
        print("=" * 80)
        print("Excel 檔案中「填單人員」欄位的前 50 筆原始資料（包含空值）：")
        print("=" * 80)
        for i, user in enumerate(df[target_col].head(50), 1):
            print(f"{i:3d}. {repr(user)}")
        
        # Forward fill
        df[target_col] = df[target_col].ffill()
        
        # 清理
        df_clean = df.dropna(subset=[target_col])
        df_clean[target_col] = df_clean[target_col].astype(str).str.strip()
        
        users = df_clean[target_col].unique().tolist()
        users = [str(u).strip() for u in users if str(u).strip() and str(u) != 'nan']
        
        print("\n" + "=" * 80)
        print("唯一人員列表（經過 ffill 清理後）：")
        print("=" * 80)
        for i, user in enumerate(sorted(users), 1):
            count = len(df_clean[df_clean[target_col] == user])
            print(f"{i:2d}. {user:20s} - {count:3d} 筆")
        
        print("\n" + "=" * 80)
        print(f"總共: {len(users)} 位人員")
        print("=" * 80)
        
        # 檢查是否有 Macro 或 Recover 開頭的人員
        test_users = [u for u in users if u.startswith('Macro') or u.startswith('Recover')]
        if test_users:
            print("\n⚠️  發現測試資料人員：")
            for u in test_users:
                print(f"   - {u}")
        
except Exception as e:
    print(f"錯誤: {e}")
    import traceback
    traceback.print_exc()
