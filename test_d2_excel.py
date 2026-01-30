import sys
sys.path.insert(0, r'C:\Users\TF000054\claude\doc_generator_v3')
from app.services.excel_parser import ExcelParser

# 測試解析最新上傳的檔案
excel_file = r'C:\Users\TF000054\claude\doc_generator_v3\uploads\temp_1769587983823_D2.xlsx'

try:
    print(f"正在解析: {excel_file}")
    result = ExcelParser.parse_work_report_excel(excel_file)
    print(f"\n解析結果:")
    print(f"  has_multiple_users: {result['has_multiple_users']}")
    print(f"  識別到的人員數: {len(result['users'])}")
    print(f"  人員列表: {result['users']}")
    
    if result['has_multiple_users']:
        print(f"\n✅ 檢測到多人員，應該生成多個簡報")
    else:
        print(f"\n⚠️  只檢測到單人員或無人員")
        
except Exception as e:
    print(f"❌ 錯誤: {e}")
    import traceback
    traceback.print_exc()
