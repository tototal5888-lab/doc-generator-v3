import os
import sys

# 可選依賴：openpyxl (用於 XLSX 讀取)
OPENPYXL_AVAILABLE = False
try:
    from openpyxl import load_workbook
    OPENPYXL_AVAILABLE = True
    print(f"[INFO] ✅ openpyxl 成功載入")
except ImportError as e:
    print(f"[WARNING] ❌ openpyxl 載入失敗 (ImportError): {e}")
    print(f"[WARNING] Python 版本: {sys.version}")
    print(f"[WARNING] Python 路徑: {sys.executable}")
except Exception as e:
    print(f"[ERROR] ❌ openpyxl 載入時發生異常: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# 可選依賴：xlrd (用於 XLS 讀取)
XLRD_AVAILABLE = False
try:
    import xlrd
    XLRD_AVAILABLE = True
    print(f"[INFO] xlrd 已載入，版本: {xlrd.__version__}")
except ImportError:
    print(f"[WARNING] xlrd 載入失敗: No module named 'xlrd'")

# 可選依賴：pywin32 (用於 XLS COM 接口)
WIN32_AVAILABLE = False
try:
    import win32com.client as win32
    import pythoncom
    WIN32_AVAILABLE = True
    print(f"[INFO] ✅ pywin32 成功載入")
except ImportError:
    print(f"[WARNING] ❌ pywin32 載入失敗")


class ExcelParser:
    """Excel 結構化解析器 - 專門用於工作報告的資料提取和分組"""
    
    # 可能的填單人員欄位名稱（關鍵字匹配）
    USER_FIELD_KEYWORDS = ['填單人員', '填單人', '需求人', '負責人', '人員', '姓名']
    
    @staticmethod
    def find_user_column(headers):
        """在標題行中尋找填單人員欄位
        
        Args:
            headers: 標題行列表
            
        Returns:
            int or None: 找到的欄位索引，未找到返回 None
        """
        for idx, header in enumerate(headers):
            if header:
                # 原始字串用於日誌
                header_raw = str(header)
                # 清理後的字串：轉小寫，去頭尾空格
                header_str = header_raw.strip().lower()
                # 移除所有內部空格（解決 "填 單 人 員" 問題）
                header_clean = header_str.replace(" ", "").replace("　", "")
                
                for keyword in ExcelParser.USER_FIELD_KEYWORDS:
                    if keyword in header_clean:
                        print(f"[DEBUG] 找到人員欄位: '{header_raw}' (匹配關鍵字: '{keyword}') at index {idx}")
                        return idx
        return None
    
    @staticmethod
    def parse_xlsx(file_path):
        """解析 XLSX 檔案
        
        Returns:
            dict: 解析結果
        """
        print(f"[ExcelParser.parse_xlsx] 開始解析: {file_path}")
        print(f"[ExcelParser.parse_xlsx] OPENPYXL_AVAILABLE = {OPENPYXL_AVAILABLE}")
        
        if not OPENPYXL_AVAILABLE:
            print(f"[ExcelParser.parse_xlsx] ❌ openpyxl 不可用，返回 None")
            return None
        
        print(f"[ExcelParser.parse_xlsx] ✅ openpyxl 可用，開始解析...")
        
        try:
            wb = load_workbook(file_path, data_only=True)
            all_records = []
            user_column = None
            headers = []
            
            for sheet_name in wb.sheetnames:
                sheet = wb[sheet_name]
                rows = list(sheet.iter_rows())
                
                if not rows:
                    continue
                
                # 尋找標題行（搜尋前 10 行）
                header_row_index = -1
                for i in range(min(len(rows), 10)):
                    row_values = [str(cell.value) if cell.value else '' for cell in rows[i]]
                    found_col = ExcelParser.find_user_column(row_values)
                    if found_col is not None:
                        headers = row_values
                        user_column = found_col
                        header_row_index = i
                        print(f"[INFO] 在工作表 '{sheet_name}' 第 {i+1} 行找到標題行，人員欄位索引: {user_column} ({headers[user_column]})")
                        break
                
                if header_row_index == -1:
                    print(f"[WARNING] 在工作表 '{sheet_name}' 前 10 行未找到包含人員關鍵字的標題行")
                    # 如果沒找到標題，嘗試預設第一行（向後兼容）
                    if rows:
                        headers = [str(cell.value) if cell.value else '' for cell in rows[0]]
                        header_row_index = 0
                
                # 處理資料行 (從標題行下一行開始)
                for row_idx, row in enumerate(rows[header_row_index+1:]):
                    row_values = [str(cell.value) if cell.value else '' for cell in row]
                    if any(row_values):  # 不是完全空白的行
                        user_val = None
                        if user_column is not None and user_column < len(row_values):
                            user_val = row_values[user_column].strip()
                            
                        record = {
                            'sheet': sheet_name,
                            'data': row_values,
                            'user': user_val
                        }
                        all_records.append(record)
            
            wb.close()
            print(f"[DEBUG] XLSX 解析完成: 找到 {len(all_records)} 條記錄")
            print(f"[DEBUG] 識別到的 headers: {headers}")
            print(f"[DEBUG] User Column Index: {user_column}")
            if user_column is not None and len(headers) > user_column:
                 print(f"[DEBUG] User Column Name: {headers[user_column]}")
            
            return {
                'headers': headers,
                'user_column': user_column,
                'records': all_records
            }
            
        except Exception as e:
            print(f"[ERROR] XLSX 解析失敗: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def parse_xls(file_path):
        """解析 XLS 檔案
        
        Returns:
            dict: 解析結果
        """
        # 優先使用 xlrd
        if XLRD_AVAILABLE:
            try:
                wb = xlrd.open_workbook(file_path)
                all_records = []
                user_column = None
                headers = []
                
                for sheet_idx in range(wb.nsheets):
                    sheet = wb.sheet_by_index(sheet_idx)
                    
                    if sheet.nrows == 0:
                        continue
                    
                    # 尋找標題行（搜尋前 10 行）
                    header_row_index = -1
                    for i in range(min(sheet.nrows, 10)):
                        row_values = [str(sheet.cell_value(i, col_idx)) for col_idx in range(sheet.ncols)]
                        found_col = ExcelParser.find_user_column(row_values)
                        if found_col is not None:
                            headers = row_values
                            user_column = found_col
                            header_row_index = i
                            print(f"[INFO] 在工作表 '{sheet.name}' 第 {i+1} 行找到標題行，人員欄位索引: {user_column} ({headers[user_column]})")
                            break
                    
                    if header_row_index == -1:
                        # 默認第一行
                        header_row_index = 0
                        params = [str(sheet.cell_value(0, col_idx)) for col_idx in range(sheet.ncols)]
                        headers = params
                    
                    # 處理資料行
                    for row_idx in range(header_row_index + 1, sheet.nrows):
                        row_values = [str(sheet.cell_value(row_idx, col_idx)) for col_idx in range(sheet.ncols)]
                        if any(row_values):  # 不是完全空白的行
                            user_val = None
                            if user_column is not None and user_column < len(row_values):
                                user_val = row_values[user_column].strip()
                                
                            record = {
                                'sheet': sheet.name,
                                'data': row_values,
                                'user': user_val
                            }
                            all_records.append(record)
                
                return {
                    'headers': headers,
                    'user_column': user_column,
                    'records': all_records
                }
                
            except Exception as e:
                print(f"[WARNING] xlrd 解析失敗: {e}")
        
        # 備用方案：使用 Excel COM 接口
        if WIN32_AVAILABLE:
            excel = None
            wb = None
            max_retries = 2
            
            for attempt in range(max_retries):
                try:
                    # 每次嘗試都重新初始化 COM
                    try:
                        pythoncom.CoUninitialize()
                    except:
                        pass
                    
                    import time
                    time.sleep(0.2)
                    
                    pythoncom.CoInitialize()
                    excel = win32.DispatchEx("Excel.Application")
                    excel.Visible = False
                    excel.DisplayAlerts = False
                    excel.Interactive = False
                    excel.ScreenUpdating = False
                    
                    abs_path = os.path.abspath(file_path)
                    # 使用 UpdateLinks=0 避免更新連結提示
                    wb = excel.Workbooks.Open(abs_path, ReadOnly=True, UpdateLinks=0)
                    
                    all_records = []
                    user_column = None
                    headers = []
                    
                    # 這裡改為分別處理每個 Sheet
                    for sheet_idx in range(1, wb.Sheets.Count + 1):
                        sheet = wb.Sheets(sheet_idx)
                        used_range = sheet.UsedRange
                        
                        if used_range is None:
                            continue
                        
                        values = used_range.Value
                        if not values:
                            continue
                        
                        # 確保 values 是 tuple list
                        if not isinstance(values, tuple):
                            values = ((values,),)
                        elif not isinstance(values[0], tuple):
                             # 單行資料
                            values = (values,)
                        
                        # 尋找標題行
                        header_row_index = -1
                        curr_sheet_headers = []
                        curr_user_column = None
                        
                        # 轉換為 list 便於處理，並處理 None
                        rows_data = []
                        for row in values:
                             rows_data.append([str(cell) if cell is not None else '' for cell in row])
                             
                        for i in range(min(len(rows_data), 10)):
                            row_strings = rows_data[i]
                            found_col = ExcelParser.find_user_column(row_strings)
                            if found_col is not None:
                                curr_sheet_headers = row_strings
                                curr_user_column = found_col
                                header_row_index = i
                                print(f"[INFO] [COM] 在工作表 '{sheet.Name}' 第 {i+1} 行找到標題行，人員欄位索引: {curr_user_column} ({curr_sheet_headers[curr_user_column]})")
                                break
                        
                        if header_row_index != -1:
                            # 更新全域資訊（假設以第一個找到的為準，雖然可能不完美）
                            if not headers:
                                headers = curr_sheet_headers
                                user_column = curr_user_column
                        else:
                            header_row_index = 0
                            if not headers and rows_data:
                                headers = rows_data[0]
                        
                        # 處理資料行
                        for row in rows_data[header_row_index+1:]:
                            if any(row):
                                user_val = None
                                if curr_user_column is not None and curr_user_column < len(row):
                                    user_val = row[curr_user_column].strip()
                                elif user_column is not None and user_column < len(row):
                                    # 嘗試使用之前找到的 user_column
                                    user_val = row[user_column].strip()
                                    
                                record = {
                                    'sheet': sheet.Name,
                                    'data': row,
                                    'user': user_val
                                }
                                all_records.append(record)
                    
                    # 成功讀取後立即清理並返回
                    try:
                        if wb:
                            wb.Close(False)
                        if excel:
                            excel.Quit()
                            del excel
                    except:
                        pass
                    
                    try:
                        pythoncom.CoUninitialize()
                    except:
                        pass
                        
                    return {
                        'headers': headers,
                        'user_column': user_column,
                        'records': all_records
                    }
                    
                except Exception as e:
                    print(f"[WARNING] XLS COM 解析嘗試 {attempt + 1}/{max_retries} 失敗: {e}")
                    
                    # 清理資源
                    try:
                        if wb:
                            wb.Close(False)
                            wb = None
                    except:
                        pass
                    try:
                        if excel:
                            excel.Quit()
                            del excel
                            excel = None
                    except:
                        pass
                    try:
                        pythoncom.CoUninitialize()
                    except:
                        pass
                    
                    # 短暫延遲後重試
                    import time
                    time.sleep(0.5)
            
            print(f"[ERROR] XLS COM 解析最終失敗")
        
        return None
    
    @staticmethod
    def group_by_user(parsed_data):
        """將解析後的資料按人員分組
        
        Args:
            parsed_data: parse_xlsx 或 parse_xls 的返回值
            
        Returns:
            dict: {
                'has_multiple_users': bool,
                'users': list,
                'data_by_user': dict,
                'all_data': str
            }
        """
        if not parsed_data or not parsed_data['records']:
            return {
                'has_multiple_users': False,
                'users': [],
                'data_by_user': {},
                'all_data': ''
            }
        
        headers = parsed_data['headers']
        records = parsed_data['records']
        user_column = parsed_data['user_column']
        
        # 收集所有人員
        users_set = set()
        for record in records:
            user = record['user']
            if user and user.strip():
                users_set.add(user)
        
        users = sorted(list(users_set))
        has_multiple_users = len(users) > 1
        
        # 按人員分組資料
        data_by_user = {}
        
        if has_multiple_users:
            for user in users:
                user_records = [r for r in records if r['user'] == user]
                data_by_user[user] = ExcelParser.format_records_as_text(headers, user_records)
        
        # 生成全部資料（向後兼容）
        all_data = ExcelParser.format_records_as_text(headers, records)
        
        print(f"[DEBUG] 分組完成: has_multiple_users={has_multiple_users}")
        print(f"[DEBUG] 識別到的人員列表 ({len(users)}位): {users}")
        
        return {
            'has_multiple_users': has_multiple_users,
            'users': users,
            'data_by_user': data_by_user,
            'all_data': all_data
        }
    
    @staticmethod
    def format_records_as_text(headers, records):
        """將記錄格式化為文字
        
        Args:
            headers: 標題列表
            records: 記錄列表
            
        Returns:
            str: 格式化後的文字
        """
        if not records:
            return ""
        
        lines = []
        current_sheet = None
        
        for record in records:
            # 如果切換到新的工作表，加上工作表標記
            if record['sheet'] != current_sheet:
                current_sheet = record['sheet']
                lines.append(f"\n=== 工作表: {current_sheet} ===")
                lines.append(" | ".join(headers))
            
            # 加入資料行
            lines.append(" | ".join(record['data']))
        
        return "\n".join(lines)
    
    @staticmethod
    def parse_work_report_excel(file_path):
        """解析工作報告 Excel，返回結構化資料
        
        Args:
            file_path: Excel 檔案路徑
            
        Returns:
            dict: {
                'has_multiple_users': bool,
                'users': list,
                'data_by_user': dict,
                'all_data': str
            }
        """
        ext = file_path.lower().split('.')[-1]
        
        parsed_data = None
        if ext == 'xlsx':
            parsed_data = ExcelParser.parse_xlsx(file_path)
        elif ext == 'xls':
            parsed_data = ExcelParser.parse_xls(file_path)
        
        if parsed_data:
            return ExcelParser.group_by_user(parsed_data)
        else:
            # 解析失敗，返回空結果
            return {
                'has_multiple_users': False,
                'users': [],
                'data_by_user': {},
                'all_data': ''
            }
