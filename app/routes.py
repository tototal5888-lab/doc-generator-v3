import os
import json
import time
from flask import Blueprint, render_template, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
from .utils.helpers import safe_filename
from .services import FileProcessor, FormatConverter, AIService
from .services.kroki_service import KrokiService
from .services.excel_parser import ExcelParser
from .services.text_parser import TextParser
from .utils.multi_user_handler import generate_multiple_work_reports

bp = Blueprint('main', __name__)

# 初始化服務 (在首次請求時或應用啟動時)
# 由於 Blueprint 在應用創建前定義，我們這裡使用延遲初始化或在視圖函數中獲取配置
# 為了簡單起見，我們在視圖函數中實例化 AIService，或者在 app context 中存儲

def get_ai_service():
    if not hasattr(current_app, 'ai_service'):
        current_app.ai_service = AIService(current_app.config)
    return current_app.ai_service

def get_prompts_by_type(doc_type):
    """從 PROMPTS_CONFIG.md 讀取指定文檔類型的 Prompt
    
    Args:
        doc_type: 文檔類型 ('system_doc', 'sop', 'work_report', 'sop_optimize')
    
    Returns:
        tuple: (optimize_prompt, generate_prompt)
               對於 sop_optimize，optimize_prompt 為 None
    """
    config_path = 'PROMPTS_CONFIG.md'
    
    if not os.path.exists(config_path):
        return None, None
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 定義文檔類型對應的標題標記
        type_headers = {
            'system_doc': '# System Doc - 系統文檔',
            'sop': '# SOP - 標準作業程序',
            'work_report': '# Work Report - 工作報告',
            'sop_optimize': '# SOP Optimize - SOP 優化'
        }
        
        if doc_type not in type_headers:
            return None, None
        
        # 找到對應文檔類型的區塊
        type_header = type_headers[doc_type]
        type_start = content.find(type_header)
        
        if type_start == -1:
            return None, None
        
        # 找到下一個文檔類型的開始位置（即當前區塊的結束位置）
        next_section = content.find('\n---\n', type_start)
        if next_section == -1:
            next_section = content.find('\n## 注意事項', type_start)
        
        if next_section == -1:
            type_section = content[type_start:]
        else:
            type_section = content[type_start:next_section]
        
        # 提取優化需求 Prompt
        optimize_prompt = None
        if doc_type != 'sop_optimize':  # sop_optimize 沒有優化需求 Prompt
            optimize_start = type_section.find('## 優化需求 Prompt')
            if optimize_start != -1:
                optimize_end = type_section.find('## 生成文檔 Prompt', optimize_start)
                if optimize_end != -1:
                    optimize_section = type_section[optimize_start:optimize_end]
                    prompt_start = optimize_section.find('```prompt\n')
                    prompt_end = optimize_section.rfind('```')
                    if prompt_start != -1 and prompt_end != -1 and prompt_start < prompt_end:
                        optimize_prompt = optimize_section[prompt_start + 10:prompt_end].strip()
        
        # 提取生成文檔 Prompt
        generate_prompt = None
        generate_start = type_section.find('## 生成文檔 Prompt')
        if generate_start != -1:
            generate_section = type_section[generate_start:]
            prompt_start = generate_section.find('```prompt\n')
            prompt_end = generate_section.rfind('```')
            if prompt_start != -1 and prompt_end != -1 and prompt_start < prompt_end:
                generate_prompt = generate_section[prompt_start + 10:prompt_end].strip()
        
        return optimize_prompt, generate_prompt
        
    except Exception as e:
        print(f"[ERROR] Failed to read prompts for {doc_type}: {e}")
        return None, None

@bp.route('/')
def index():
    return render_template('index_v3_daisy.html')

@bp.route('/help')
def help_page():
    return render_template('help.html')

@bp.route('/prompt-manager')
def prompt_manager():
    return render_template('prompt_manager.html')

@bp.route('/api/help', methods=['GET'])
def get_help():
    """獲取幫助文檔內容"""
    try:
        help_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'PROJECT_ARCHITECTURE.md')
        
        if not os.path.exists(help_file_path):
            return jsonify({"success": False, "error": "幫助文檔不存在"}), 404
        
        with open(help_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            "success": True,
            "content": content
        })
    except Exception as e:
        current_app.logger.error(f"讀取幫助文檔失敗: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@bp.route('/api/config', methods=['GET', 'POST'])
def api_config():
    ai_service = get_ai_service()
    if request.method == 'POST':
        config = request.json
        ai_service.save_api_config(config)
        return jsonify({"success": True, "message": "配置已保存"})
    else:
        return jsonify(ai_service.load_api_config())

@bp.route('/api/verify-password', methods=['POST'])
def verify_password():
    """驗證管理員密碼"""
    try:
        data = request.json
        password = data.get('password', '')
        
        # 從配置中獲取正確的密碼
        correct_password = current_app.config.get('ADMIN_PASSWORD', 'sunon')
        
        if password == correct_password:
            return jsonify({"success": True, "message": "密碼正確"})
        else:
            return jsonify({"success": False, "message": "密碼錯誤"}), 401
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in inject_images: {error_details}")
        return jsonify({"success": False, "error": str(e)}), 500

@bp.route('/api/upload_template', methods=['POST'])
def upload_template():
    if 'file' not in request.files:
        return jsonify({"error": "沒有文件部分"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "未選擇文件"}), 400
        
    if file:
        filename = safe_filename(file.filename)
        # 確保文件名不重複
        base, ext = os.path.splitext(filename)
        timestamp = int(time.time())
        filename = f"{base}_{timestamp}{ext}"
        
        folder = current_app.config['TEMPLATE_STORAGE_FOLDER']
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        save_path = os.path.join(folder, filename)
        file.save(save_path)
        
        return jsonify({
            "success": True, 
            "filename": filename,
            "path": save_path,
            "message": "上傳成功"
        })

@bp.route('/api/templates', methods=['GET'])
def list_templates():
    templates = []
    folder = current_app.config['TEMPLATE_STORAGE_FOLDER']
    if os.path.exists(folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                # 獲取文件信息
                stats = os.stat(file_path)
                ext = os.path.splitext(filename)[1].lower().replace('.', '')
                
                templates.append({
                    "filename": filename,
                    "type": ext.upper(),
                    "size": stats.st_size,
                    "modified": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stats.st_mtime))
                })
    return jsonify(templates)


@bp.route('/api/download_template/<filename>', methods=['GET'])
def download_template(filename):
    """下載模板原始檔案"""
    try:
        folder = current_app.config['TEMPLATE_STORAGE_FOLDER']
        file_path = os.path.join(folder, filename)
        
        if not os.path.exists(file_path):
            return jsonify({"success": False, "error": "模板文件不存在"}), 404
        
        return send_file(file_path, as_attachment=True, download_name=filename)
    except Exception as e:
        current_app.logger.error(f"下載模板失敗: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route('/api/delete_template/<filename>', methods=['DELETE'])
def delete_template(filename):
    try:
        filename = safe_filename(filename)
        folder = current_app.config['TEMPLATE_STORAGE_FOLDER']
        file_path = os.path.join(folder, filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({"success": True, "message": "模板已刪除"})
        else:
            return jsonify({"success": False, "error": "文件不存在"}), 404
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@bp.route('/api/prompts', methods=['GET', 'POST'])
def manage_prompts():
    """管理所有文檔類型的 Prompt 配置"""
    try:
        config_path = 'PROMPTS_CONFIG.md'
        
        if request.method == 'GET':
            # 讀取 Prompt 配置
            doc_type = request.args.get('doc_type', 'work_report')
            
            if not os.path.exists(config_path):
                return jsonify({"success": False, "error": "配置檔案不存在"}), 404
            
            # 使用 get_prompts_by_type 函數讀取
            optimize_prompt, generate_prompt = get_prompts_by_type(doc_type)
            
            # sop_optimize 沒有優化需求 Prompt
            has_optimize = doc_type != 'sop_optimize'
            
            return jsonify({
                "success": True,
                "doc_type": doc_type,
                "optimize_prompt": optimize_prompt or "",
                "generate_prompt": generate_prompt or "",
                "has_optimize": has_optimize
            })
        
        elif request.method == 'POST':
            # 儲存 Prompt 配置
            data = request.json
            doc_type = data.get('doc_type', 'work_report')
            optimize_prompt = data.get('optimize_prompt', '').strip()
            generate_prompt = data.get('generate_prompt', '').strip()
            
            # 驗證：sop_optimize 只需要生成文檔 Prompt
            if doc_type == 'sop_optimize':
                if not generate_prompt:
                    return jsonify({"success": False, "error": "生成文檔 Prompt 不能為空"}), 400
            else:
                if not optimize_prompt or not generate_prompt:
                    return jsonify({"success": False, "error": "Prompt 內容不能為空"}), 400
            
            # 讀取現有配置檔案
            if not os.path.exists(config_path):
                return jsonify({"success": False, "error": "配置檔案不存在"}), 404
            
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 找到要更新的文檔類型區塊
            type_headers = {
                'system_doc': '# System Doc - 系統文檔',
                'sop': '# SOP - 標準作業程序',
                'work_report': '# Work Report - 工作報告',
                'sop_optimize': '# SOP Optimize - SOP 優化'
            }
            
            if doc_type not in type_headers:
                return jsonify({"success": False, "error": "不支援的文檔類型"}), 400
            
            type_header = type_headers[doc_type]
            type_start = content.find(type_header)
            
            if type_start == -1:
                return jsonify({"success": False, "error": f"找不到 {doc_type} 的配置區塊"}), 400
            
            # 找到下一個文檔類型的開始位置
            next_section = content.find('\n---\n', type_start + len(type_header))
            if next_section == -1:
                next_section = content.find('\n## 注意事項', type_start)
            
            # 構建新的區塊內容
            if doc_type == 'sop_optimize':
                # SOP Optimize 只有生成文檔 Prompt
                new_section = f"""{type_header}

## 生成文檔 Prompt

```prompt
{generate_prompt}
```
"""
            else:
                # 其他類型有兩個 Prompt
                new_section = f"""{type_header}

## 優化需求 Prompt

```prompt
{optimize_prompt}
```

## 生成文檔 Prompt

```prompt
{generate_prompt}
```
"""
            
            # 替換舊的區塊內容
            if next_section == -1:
                # 最後一個區塊
                new_content = content[:type_start] + new_section
            else:
                new_content = content[:type_start] + new_section + content[next_section:]
            
            # 儲存文件
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return jsonify({
                "success": True,
                "message": f"{type_headers[doc_type]} 的 Prompt 配置已儲存"
            })
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        current_app.logger.error(f"管理 Prompt 失敗: {error_details}")
        return jsonify({"success": False, "error": str(e)}), 500

@bp.route('/api/optimize-requirements', methods=['POST'])
def optimize_requirements():
    """使用 AI 優化需求描述"""
    try:
        data = request.json
        requirements = data.get('requirements', '').strip()
        doc_type = data.get('doc_type', 'system_doc')

        if not requirements:
            return jsonify({"success": False, "error": "需求描述不能為空"}), 400

        # 獲取 AI 服務
        ai_service = get_ai_service()

        # 1.5 讀取 Profile (角色設定)
        profile_content = ""
        try:
            # 根據文檔類型選擇 Profile
            if doc_type in ['sop', 'sop_optimize']:
                profile_path = 'PTT_PROFILE.md'
            else:
                profile_path = 'SYS_PROFILE.md'
            
            # 讀取 Profile 內容
            if os.path.exists(profile_path):
                with open(profile_path, 'r', encoding='utf-8') as f:
                    profile_content = f.read()
                # 添加分隔線，確保 AI 區分角色設定與具體指令
                profile_content = f"{profile_content}\n\n=== Role Definition End ===\n\n"
                print(f"[INFO] Loaded profile from {profile_path}")
            else:
                print(f"[WARNING] Profile {profile_path} not found")
                
        except Exception as e:
            print(f"[ERROR] Failed to read profile: {e}")

        # 從 PROMPTS_CONFIG.md 讀取 Prompt（所有類型統一處理）
        optimize_prompt_template, _ = get_prompts_by_type(doc_type)
        
        if optimize_prompt_template:
            # 使用從配置檔案讀取的 Prompt
            optimize_prompt = profile_content + "\n\n" + optimize_prompt_template.replace('{requirements}', requirements)
        else:
            # 如果讀取失敗，使用預設的 Prompt（向後兼容）
            if doc_type == 'sop':
                role_def = "你現在是一位企業內部系統的 SOP 工程師，熟悉採購/廠商報價/審核流程。"
                if profile_content:
                    role_def = ""
                
                optimize_prompt = f"""
{profile_content}
{role_def}
輸出語言：繁體中文。

請依照我提供的功能模組，產生標準 SOP 文件。

規則：
1. SOP 請保持明確、實務、不要誇大或補造不存在的功能。
2. 每段 SOP 都需包含以下章節：
   (A) 作業目的
   (B) 使用角色
   (C) 系統流程圖（文字描述即可）
   (D) 作業流程步驟（逐步條列）
   (E) 異常處理 / 錯誤訊息處理
   (F) 注意事項
3. 若流程中涉及 UI 操作，請加入畫面邏輯（例如：點選「新增報價」、輸入欄位、按下儲存）。
4. 內容需保持一致性、準確描述流程，不可幻想不存在的系統功能。
5. 使用 Markdown 格式輸出。

原始需求：
{requirements}

請依照上述規則，產生標準 SOP 文件："""
            
            elif doc_type == 'system_doc':
                optimize_prompt = f"""
{profile_content}
請優化以下系統文檔的需求描述，使其更加清晰、完整、專業。

原始需求：
{requirements}

請提供優化後的需求描述，要求：
1. 補充系統架構資訊（前端、後端、資料庫）
2. 明確功能模組劃分
3. 列出技術棧需求
4. 包含部署和維護說明
5. 使用專業術語，結構清晰
6. 使用 Markdown 格式輸出

優化後的需求描述："""
            
            else:
                # work_report 和其他類型的預設 Prompt
                optimize_prompt = f"""
{profile_content}
請優化以下需求描述，使其更加清晰、完整、專業。

原始需求：
{requirements}

請提供優化後的需求描述，要求：
1. 保持原意，補充必要的細節
2. 使用專業術語
3. 結構清晰，分點說明
4. 使用 Markdown 格式輸出

優化後的需求描述："""

        # 調用 AI API
        optimized_text, usage_info = ai_service.generate_content(optimize_prompt)

        return jsonify({
            "success": True,
            "optimized_requirements": optimized_text.strip(),
            "original_requirements": requirements
        })

    except Exception as e:
        current_app.logger.error(f"優化需求失敗: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@bp.route('/api/generate', methods=['POST'])
def generate_document():
    try:
        data = request.json
        doc_type = data.get('doc_type')
        template_file = data.get('template') # 前端傳過來的是 template
        user_requirements = data.get('requirements')
        output_format = data.get('output_format', 'pptx')
        image_folder_name = data.get('image_folder')  # 從前端獲取圖片文件夾名稱
        
        # 特殊處理：檢查是否為工作報告 Excel 並需要多人員拆分
        upload_folder = current_app.config['UPLOAD_FOLDER']
        excel_file_path = None
        
        # 方式 1：如果 user_requirements 看起來像檔名，檢查該文件
        if doc_type == 'work_report' and user_requirements:
            if user_requirements.endswith(('.xlsx', '.xls')):
                req_file_path = os.path.join(upload_folder, user_requirements)
                if os.path.exists(req_file_path):
                    excel_file_path = req_file_path
                    print(f"[INFO] 檢測到 Excel 檔名: {user_requirements}")
        
        # 方式 2：查找 uploads 資料夾中最新的 Excel 文件（用戶上傳後的情況）
        if not excel_file_path and doc_type == 'work_report':
            try:
                # 查找所有 temp_*.xlsx 和 temp_*.xls 文件
                import glob
                excel_patterns = [
                    os.path.join(upload_folder, 'temp_*.xlsx'),
                    os.path.join(upload_folder, 'temp_*.xls')
                ]
                excel_files = []
                for pattern in excel_patterns:
                    excel_files.extend(glob.glob(pattern))
                
                # 找到最新的文件
                if excel_files:
                    excel_file_path = max(excel_files, key=os.path.getmtime)
                    print(f"[INFO] 找到最新的 Excel 文件: {excel_file_path}")
            except Exception as e:
                print(f"[WARNING] 查找 Excel 文件失敗: {e}")
        
        # 如果找到 Excel 文件，嘗試多人員處理
        if excel_file_path and os.path.exists(excel_file_path):
            print(f"[DEBUG] ========== 開始 Excel 多人員檢測流程 ==========")
            print(f"[DEBUG] Excel 檔案路徑: {excel_file_path}")
            print(f"[DEBUG] 檔案大小: {os.path.getsize(excel_file_path)} bytes")
            print(f"[DEBUG] 文檔類型: {doc_type}")
            print(f"[DEBUG] 模板檔案: {template_file}")
            print(f"[DEBUG] 輸出格式: {output_format}")
            
            try:
                # 嘗試自動轉換 XLS -> XLSX (對於多人員檢測流程)
                if excel_file_path.lower().endswith('.xls'):
                    print(f"[INFO] 檢測到 XLS 文件，嘗試轉換為 XLSX 以獲得更穩定的解析: {excel_file_path}")
                    xlsx_path = excel_file_path.replace('.xls', '.xlsx')
                    
                    # 如果 XLSX 已經存在（無論是否由 extract_text 生成），優先使用
                    if os.path.exists(xlsx_path):
                        print(f"[INFO] 發現對應的 XLSX 文件，切換使用: {xlsx_path}")
                        excel_file_path = xlsx_path
                    else:
                        # 嘗試轉換
                        try:
                            import win32com.client as win32
                            import pythoncom
                            
                            excel = None
                            wb = None
                            try:
                                pythoncom.CoInitialize()
                                excel = win32.DispatchEx("Excel.Application")
                                excel.Visible = False
                                excel.DisplayAlerts = False
                                
                                abs_path = os.path.abspath(excel_file_path)
                                abs_out_path = os.path.abspath(xlsx_path)
                                
                                wb = excel.Workbooks.Open(abs_path, ReadOnly=True, UpdateLinks=False)
                                wb.SaveAs(abs_out_path, FileFormat=51) # 51 = xlOpenXMLWorkbook
                                wb.Close(False)
                                excel.Quit()
                                
                                print(f"[SUCCESS] 成功將 XLS 轉換為 XLSX，切換使用: {xlsx_path}")
                                excel_file_path = xlsx_path
                                
                                # 刪除原始 XLS 以避免混淆（可選）
                                try:
                                    import time
                                    time.sleep(0.5)
                                    if os.path.exists(excel_file_path.replace('.xlsx', '.xls')):
                                        # 這裡要注意不要刪錯，因為現在 excel_file_path 已經是 xlsx
                                        pass
                                except:
                                    pass
                                    
                            except Exception as com_err:
                                print(f"[WARNING] 多人員檢測時 XLS 轉換失敗: {com_err}")
                            finally:
                                try:
                                    if wb: wb.Close(False)
                                    if excel: excel.Quit()
                                except: pass
                                pythoncom.CoUninitialize()
                        except Exception as e:
                            print(f"[WARNING] 轉換過程發生錯誤: {e}")

                print(f"[INFO] 開始解析 Excel: {excel_file_path}")
                excel_data = ExcelParser.parse_work_report_excel(excel_file_path)
                
                print(f"[INFO] ========== Excel 解析結果 ==========")
                print(f"[INFO] has_multiple_users: {excel_data['has_multiple_users']}")
                print(f"[INFO] 人員數量: {len(excel_data['users'])}")
                print(f"[INFO] 人員列表: {excel_data['users']}")
                print(f"[INFO] data_by_user keys: {list(excel_data.get('data_by_user', {}).keys())}")
                
                if excel_data['has_multiple_users']:
                    # 多人員：呼叫多人員處理函數
                    print(f"[INFO] ========== 啟動多人員處理流程 ==========")
                    print(f"[INFO] 檢測到多人員({len(excel_data['users'])}位)，準備生成多個簡報")
                    print(f"[INFO] 模板: {template_file}, 格式: {output_format}")
                    
                    result = generate_multiple_work_reports(excel_data, template_file, output_format, image_folder_name)
                    
                    print(f"[INFO] ========== 多人員處理完成 ==========")
                    print(f"[INFO] 返回結果類型: {type(result)}")
                    
                    return result
                else:
                    print(f"[INFO] 單人員或無人員欄位，使用標準流程")
            except Exception as e:
                print(f"[ERROR] ========== Excel 多人員檢測失敗 ==========")
                print(f"[ERROR] 錯誤訊息: {e}")
                print(f"[ERROR] 錯誤類型: {type(e).__name__}")
                import traceback
                traceback.print_exc()
                print(f"[ERROR] ========== 錯誤堆疊結束 ==========")
                # 不要中斷，讓程序繼續執行標準流程
        
        # 方式 3：檢查文字檔是否包含多人員標記
        if doc_type == 'work_report' and not excel_file_path and user_requirements:
            try:
                print(f"[INFO] 開始分析文字內容是否包含多人員標記")
                text_data = TextParser.parse_work_report_text(user_requirements)
                
                print(f"[INFO] 文字解析結果: has_multiple_users={text_data['has_multiple_users']}, users={text_data['users']}")
                
                if text_data['has_multiple_users']:
                    # 多人員：呼叫多人員處理函數
                    print(f"[INFO] 文字檔檢測到多人員({len(text_data['users'])}位)，啟動多人員處理")
                    return generate_multiple_work_reports(text_data, template_file, output_format, image_folder_name)
                else:
                    print(f"[INFO] 文字檔為單人員或無人員標記，使用標準流程")
            except Exception as e:
                print(f"[ERROR] 文字檔多人員檢測失敗: {e}")
                import traceback
                traceback.print_exc()
        
        if not all([doc_type, template_file, user_requirements]):
            return jsonify({"error": "缺少必要參數"}), 400
            
        # 1. 讀取模板內容
        template_path = os.path.join(current_app.config['TEMPLATE_STORAGE_FOLDER'], template_file)
        if not os.path.exists(template_path):
            return jsonify({"error": "模板文件不存在"}), 404
            
        template_content = FileProcessor.extract_text(template_path)
        
        # 1.5 讀取 Profile (角色設定)
        profile_content = ""
        try:
            # 根據文檔類型選擇 Profile
            if doc_type in ['sop', 'sop_optimize']:
                profile_path = 'PTT_PROFILE.md'
            else:
                profile_path = 'SYS_PROFILE.md'
            
            # 讀取 Profile 內容
            if os.path.exists(profile_path):
                with open(profile_path, 'r', encoding='utf-8') as f:
                    profile_content = f.read()
                # 添加分隔線，確保 AI 區分角色設定與具體指令
                profile_content = f"{profile_content}\n\n=== Role Definition End ===\n\n"
                print(f"[INFO] Loaded profile from {profile_path}")
            else:
                print(f"[WARNING] Profile {profile_path} not found")
                
        except Exception as e:
            print(f"[ERROR] Failed to read profile: {e}")

        # 2. 構建 Prompt
        prompts = {
            "system_doc": {
                "name": "系統文檔",
                "prompt": f"""
{profile_content}
請根據以下模板結構和用戶需求，生成一份專業的系統文檔。

模板內容：
{template_content}

用戶需求：
{user_requirements}

要求：
1. 保持專業的技術文檔風格
2. 包含系統架構、功能模組、技術棧等內容
3. 確保文檔結構清晰、邏輯嚴謹
4. 使用標準的技術術語
5. 根據模板格式調整輸出格式
6. 請生成完整的系統文檔內容，使用Markdown格式輸出。
                """,
                "title": "系統設計文檔"
            },
            "sop": {
                "name": "SOP標準作業程序",
                "prompt": f"""
{profile_content}
請根據以下模板結構和用戶需求，生成一份標準作業程序(SOP)文檔。

模板內容：
{template_content}

用戶需求：
{user_requirements}

要求：
1. 步驟清晰明確
2. 包含目的、範圍、職責、流程圖（文字描述）、詳細步驟
3. 注意事項和異常處理
4. 語言簡練、指令性強
5. 根據模板格式調整輸出格式
6. 請生成完整的SOP內容，使用Markdown格式輸出。
                """,
                "title": "標準作業程序(SOP)"
            },
            "work_report": {
                "name": "工作報告",
                "prompt": None,  # Will be set below
                "title": "ERP工作報告"
            },
            "sop_optimize": {
                "name": "SOP優化",
                "prompt": f"""
{profile_content}
你是一位專業的 SOP 文檔優化專家。請將以下舊的 SOP 文檔優化為統一、專業的標準作業程序。

=== 原始 SOP 內容 ===
{user_requirements}

=== 參考模板風格 ===
{template_content}

=== 優化要求 ===

**1. 內容處理原則**：
- **保留所有關鍵信息**：所有操作步驟、設定值、路徑、注意事項都必須保留
- **保留所有圖片標記**：格式為 [圖片 X-Y: 來自投影片 Z]，必須完整保留
- **允許合理整合**：可以整合重複或相似的內容，使文檔更簡潔
- **保留業務邏輯**：確保所有業務流程和邏輯關係都清晰呈現

**2. 圖片標記處理**：
- 所有 [圖片 X-Y: 來自投影片 Z] 標記必須保留
- 圖片標記應放在相關內容的適當位置
- 不要刪除任何圖片標記

**3. 格式優化**：
- 參考模板的章節結構（目的、範圍、職責、流程等）
- 使用清晰的標題層級（#, ##, ###）
- 使用列表和表格提高可讀性
- 統一術語和表達方式

**4. 內容組織**：
- 將內容按照標準 SOP 結構重新組織
- 合併重複的說明，但保留所有獨特的信息
- 確保邏輯清晰、步驟連貫
- 使用適當的章節劃分

**5. 語言優化**：
- 使用專業、簡練的語言
- 統一術語
- 改善可讀性
- 消除冗餘表達

**輸出格式**：
- 使用 Markdown 格式
- 清晰的標題層級
- 適當使用列表和表格

請生成優化後的 SOP 文檔，確保所有關鍵信息和圖片標記都被保留。
                """,
                "title": "SOP優化文檔"
            }
        }
        
        doc_config = prompts.get(doc_type)
        if not doc_config:
            return jsonify({"error": "不支持的文檔類型"}), 400
        
        # 從 PROMPTS_CONFIG.md 讀取對應文檔類型的生成 Prompt（統一處理）
        _, generate_prompt_template = get_prompts_by_type(doc_type)
        
        if generate_prompt_template:
            # 使用從配置檔案讀取的 Prompt，替換變數
            prompt_with_vars = generate_prompt_template.replace('{user_requirements}', user_requirements)
            prompt_with_vars = prompt_with_vars.replace('{template_content}', template_content)
            doc_config['prompt'] = profile_content + "\n\n" + prompt_with_vars
        elif doc_config.get('prompt'):
            # 如果配置檔案讀取失敗，使用程式碼中預設的 Prompt（向後兼容）
            pass  # 保留原始 prompt
        else:
            # 如果兩者都沒有，返回錯誤
            return jsonify({"error": f"無法載入 {doc_type} 的 Prompt 配置"}), 500
            
        # 3. 調用 AI 生成內容
        ai_service = get_ai_service()
        generated_content, usage_info = ai_service.generate_content(doc_config['prompt'])
        
        # 4. 格式轉換與保存
        from datetime import datetime
        datetime_str = datetime.now().strftime('%Y%m%d%H%M%S')  # 格式：YYYYMMDDHHMMSS
        
        # 生成文件名：如果是 SOP 優化，保留原文件名
        if doc_type == 'sop_optimize':
            # 從 template_file 提取原始文件名（去除擴展名）
            original_name = os.path.splitext(template_file)[0]
            base_filename = f"{original_name}_{datetime_str}"
        else:
            # 其他類型使用日期時間格式
            base_filename = f"generated_{doc_type}_{datetime_str}"
        
        output_folder = current_app.config['OUTPUT_FOLDER']
        
        result_files = {}
        
        # 始終保存 Markdown 原文
        md_filename = f"{base_filename}.md"
        md_path = os.path.join(output_folder, md_filename)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(generated_content)
        result_files['md'] = md_filename
        
        # 根據請求的格式轉換
        if output_format == 'docx':
            docx_filename = f"{base_filename}.docx"
            docx_path = os.path.join(output_folder, docx_filename)
            # 傳遞模板路徑，讓生成的文檔繼承模板的樣式和背景
            doc = FormatConverter.markdown_to_docx(generated_content, doc_config, template_path)
            doc.save(docx_path)
            result_files['docx'] = docx_filename
            download_file = docx_filename
            
        elif output_format == 'pptx':
            pptx_filename = f"{base_filename}.pptx"
            pptx_path = os.path.join(output_folder, pptx_filename)
            
            # 如果有圖片文件夾，傳遞給轉換器
            image_folder_path = None
            if image_folder_name:
                image_folder_path = os.path.join(output_folder, 'temp_images', image_folder_name)
                print(f"[DEBUG] 圖片文件夾路徑: {image_folder_path}")
                print(f"[DEBUG] 文件夾是否存在: {os.path.exists(image_folder_path)}")
            else:
                print(f"[DEBUG] 沒有收到 image_folder_name")
            
            # 傳遞模板路徑，讓生成的簡報繼承模板的母片樣式和背景
            prs = FormatConverter.markdown_to_pptx(generated_content, doc_config, image_folder_path, template_path)
            prs.save(pptx_path)
            result_files['pptx'] = pptx_filename
            download_file = pptx_filename
            
        elif output_format == 'pdf':
            pdf_filename = f"{base_filename}.pdf"
            pdf_path = os.path.join(output_folder, pdf_filename)
            FormatConverter.markdown_to_pdf(generated_content, doc_config, pdf_path)
            result_files['pdf'] = pdf_filename
            download_file = pdf_filename
            
        else: # 默認 Markdown
            download_file = md_filename
            
        return jsonify({
            "success": True,
            "message": "文檔生成成功",
            "filename": download_file,
            "format": output_format,
            "files": result_files,
            "usage": usage_info,
            "download_url": f"/api/download/{download_file}",
            "preview": generated_content[:500] + "..."
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@bp.route('/api/download/<filename>')
def download_file(filename):
    return send_file(
        os.path.join(current_app.config['OUTPUT_FOLDER'], filename),
        as_attachment=True
    )

@bp.route('/api/generated_documents', methods=['GET'])
def generated_documents():
    files = []
    folder = current_app.config['OUTPUT_FOLDER']
    if os.path.exists(folder):
        # 按修改時間排序
        paths = sorted(
            [os.path.join(folder, f) for f in os.listdir(folder)],
            key=os.path.getmtime,
            reverse=True
        )
        
        for path in paths:
            if os.path.isfile(path):
                filename = os.path.basename(path)
                # 只顯示生成的文件
                if filename.startswith('generated_'):
                    ext = filename.split('.')[-1].upper()
                    stats = os.stat(path)
                    files.append({
                        "filename": filename,
                        "format": ext,
                        "size": stats.st_size,
                        "created": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stats.st_mtime))
                    })
    return jsonify(files)

@bp.route('/api/history')
def history():
    files = []
    folder = current_app.config['OUTPUT_FOLDER']
    if os.path.exists(folder):
        # 按修改時間排序
        paths = sorted(
            [os.path.join(folder, f) for f in os.listdir(folder)],
            key=os.path.getmtime,
            reverse=True
        )
        
        for path in paths:
            if os.path.isfile(path):
                filename = os.path.basename(path)
                # 只顯示生成的文件
                if filename.startswith('generated_'):
                    ext = filename.split('.')[-1]
                    files.append({
                        "filename": filename,
                        "type": ext,
                        "date": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(path))),
                        "size": f"{os.path.getsize(path) / 1024:.1f} KB"
                    })
    return jsonify(files)

@bp.route('/api/delete_generated/<filename>', methods=['DELETE'])
def delete_generated_document(filename):
    try:
        filename = safe_filename(filename)
        folder = current_app.config['OUTPUT_FOLDER']
        file_path = os.path.join(folder, filename)
        
        # 只允許刪除 generated_ 開頭的文件
        if not filename.startswith('generated_'):
            return jsonify({"success": False, "error": "只能刪除生成的文件"}), 403
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({"success": True, "message": "文件已刪除"})
        else:
            return jsonify({"success": False, "error": "文件不存在"}), 404
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@bp.route('/api/batch_delete_generated', methods=['POST'])
def batch_delete_generated():
    try:
        data = request.json
        filenames = data.get('filenames', [])
        
        if not filenames:
            return jsonify({"success": False, "error": "未選擇文件"}), 400
        
        folder = current_app.config['OUTPUT_FOLDER']
        deleted_count = 0
        errors = []
        
        for filename in filenames:
            filename = safe_filename(filename)
            
            # 只允許刪除 generated_ 開頭的文件
            if not filename.startswith('generated_'):
                errors.append(f"{filename}: 只能刪除生成的文件")
                continue
            
            file_path = os.path.join(folder, filename)
            
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except Exception as e:
                    errors.append(f"{filename}: {str(e)}")
            else:
                errors.append(f"{filename}: 文件不存在")
        
        if deleted_count > 0:
            message = f"成功刪除 {deleted_count} 個文件"
            if errors:
                message += f"，{len(errors)} 個失敗"
            return jsonify({"success": True, "message": message, "deleted": deleted_count, "errors": errors})
        else:
            return jsonify({"success": False, "error": "沒有文件被刪除", "errors": errors}), 400
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@bp.route('/api/extract_text', methods=['POST'])
def extract_text():
    """提取上傳文件的文本內容（PPTX 文件會同時提取圖片）"""
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "未上傳文件"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"success": False, "error": "未選擇文件"}), 400
        
        
        # 保存臨時文件（使用時間戳避免衝突）
        import time
        filename = safe_filename(file.filename)
        temp_folder = current_app.config['UPLOAD_FOLDER']
        timestamp = int(time.time() * 1000)  # 毫秒級時間戳
        temp_path = os.path.join(temp_folder, f"temp_{timestamp}_{filename}")
        
        # 如果文件存在（不太可能，但以防萬一），先刪除
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        
        file.save(temp_path)
        
        
        try:
            ext = filename.lower().split('.')[-1]
            content = ""
            image_info = None
            
            # 如果是 XLS，自動轉換為 XLSX（更穩定）
            if ext == 'xls':
                print(f"[INFO] 檢測到 .xls 文件，嘗試自動轉換為 .xlsx...")
                converted_path = temp_path.replace('.xls', '.xlsx')
                
                try:
                    # 嘗試使用 Excel COM 轉換
                    import win32com.client as win32
                    import pythoncom
                    
                    excel = None
                    wb = None
                    try:
                        pythoncom.CoInitialize()
                        excel = win32.DispatchEx("Excel.Application")
                        excel.Visible = False
                        excel.DisplayAlerts = False
                        
                        abs_temp_path = os.path.abspath(temp_path)
                        wb = excel.Workbooks.Open(abs_temp_path, ReadOnly=True, UpdateLinks=False)
                        
                        # 另存為 XLSX (51 = xlOpenXMLWorkbook)
                        abs_converted_path = os.path.abspath(converted_path)
                        wb.SaveAs(abs_converted_path, FileFormat=51)
                        wb.Close(False)
                        excel.Quit()
                        
                        print(f"[SUCCESS] 已成功轉換為 .xlsx 格式")
                        
                        # 刪除原始 XLS 文件
                        try:
                            import time
                            time.sleep(0.2)
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                        except:
                            pass
                        
                        # 使用轉換後的文件
                        temp_path = converted_path
                        filename = os.path.basename(converted_path)
                        ext = 'xlsx'
                        
                    finally:
                        try:
                            if wb:
                                wb.Close(False)
                            if excel:
                                excel.Quit()
                                del excel
                        except:
                            pass
                        pythoncom.CoUninitialize()
                        
                except Exception as convert_error:
                    print(f"[WARNING] XLS 轉換失敗: {convert_error}")
                    print("[INFO] 將使用原始 XLS 文件繼續處理")
            
            # 如果是 PPTX，提取圖片
            if ext == 'pptx':
                from app.services.image_service import ImageExtractor
                
                # 提取文本（包含圖片標記）
                content, image_count = FileProcessor.extract_text_from_pptx(temp_path, include_image_markers=True)
                
                # 如果有圖片，提取並保存
                if image_count > 0:
                    # 創建臨時圖片文件夾
                    base_image_folder = os.path.join(current_app.config['OUTPUT_FOLDER'], 'temp_images')
                    image_folder = ImageExtractor.create_temp_image_folder(base_image_folder)
                    
                    # 提取圖片
                    images = ImageExtractor.extract_images_from_pptx(temp_path, image_folder)
                    
                    image_info = {
                        'count': image_count,
                        'folder': image_folder,
                        'images': images
                    }
            else:
                # 其他格式使用原有邏輯
                content = FileProcessor.extract_text(temp_path)
            
            # 嘗試刪除臨時文件（容錯處理）
            try:
                # 添加短暫延遲，讓文件句柄完全釋放
                import time
                time.sleep(0.1)
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except PermissionError as pe:
                # Windows 文件鎖定問題，記錄警告但不中斷
                print(f"[WARNING] 無法刪除臨時文件 {temp_path}: {pe}")
                print("[INFO] 文件將在下次清理時移除")
            except Exception as e:
                print(f"[WARNING] 刪除臨時文件時發生錯誤: {e}")
            
            response_data = {
                "success": True,
                "content": content,
                "filename": filename
            }
            
            # 如果有圖片信息，添加到響應中
            if image_info:
                response_data['images'] = {
                    'count': image_info['count'],
                    'folder': os.path.basename(image_info['folder'])  # 只返回文件夾名稱
                }
            
            return jsonify(response_data)
            
        except Exception as e:
            # 確保嘗試刪除臨時文件（容錯）
            try:
                if os.path.exists(temp_path):
                    import time
                    time.sleep(0.1)
                    os.remove(temp_path)
            except:
                print(f"[WARNING] 清理臨時文件失敗: {temp_path}")
            # 打印詳細錯誤訊息
            import traceback
            print(f"[ERROR] extract_text 內部錯誤: {e}")
            print(traceback.format_exc())
            raise e
            
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"[ERROR] extract_text 失敗: {error_msg}")
        print(traceback.format_exc())
        return jsonify({"success": False, "error": error_msg}), 500

@bp.route('/api/stage_image', methods=['POST'])
def stage_image():
    """暫存圖片用於後續注入"""
    try:
        if 'image' not in request.files:
            return jsonify({"success": False, "error": "沒有上傳圖片"}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({"success": False, "error": "文件名為空"}), 400
        
        # 創建暫存目錄
        temp_dir = os.path.join(current_app.config['OUTPUT_FOLDER'], 'temp_images')
        os.makedirs(temp_dir, exist_ok=True)
        
        # 保存文件
        filename = safe_filename(file.filename)
        timestamp = int(time.time() * 1000)
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(temp_dir, unique_filename)
        file.save(file_path)
        
        return jsonify({
            "success": True,
            "filename": unique_filename,
            "path": file_path
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@bp.route('/api/inject_images', methods=['POST'])
def inject_images():
    """將圖片注入到指定的 PPTX 文件"""
    try:
        from .services.ppt_injector import PPTXInjector
        
        data = request.json
        source_filename = data.get('filename')
        injections = data.get('injections', [])
        
        if not source_filename:
            return jsonify({"success": False, "error": "未指定源文件"}), 400
        
        if not injections:
            return jsonify({"success": False, "error": "未指定圖片注入配置"}), 400
        
        # 構建源文件路徑
        source_path = os.path.join(current_app.config['OUTPUT_FOLDER'], source_filename)
        
        if not os.path.exists(source_path):
            return jsonify({"success": False, "error": "源文件不存在"}), 404
        
        # 執行圖片注入
        output_path = PPTXInjector.inject_images(source_path, injections)
        output_filename = os.path.basename(output_path)
        
        return jsonify({
            "success": True,
            "filename": output_filename,
            "download_url": f"/api/download/{output_filename}"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============= 流程圖生成 API =============

def get_kroki_service():
    """獲取 Kroki 服務實例"""
    if not hasattr(current_app, 'kroki_service'):
        output_folder = current_app.config['OUTPUT_FOLDER']
        current_app.kroki_service = KrokiService(output_folder)
    return current_app.kroki_service


@bp.route('/api/generate-mermaid', methods=['POST'])
def generate_mermaid():
    """使用 AI 將流程描述轉換為 Mermaid code"""
    try:
        data = request.json
        description = data.get('description', '').strip()
        
        if not description:
            return jsonify({"success": False, "error": "流程描述不能為空"}), 400
        
        # 獲取服務
        ai_service = get_ai_service()
        kroki_service = get_kroki_service()
        
        # 生成 prompt
        prompt = kroki_service.generate_mermaid_prompt(description)
        
        # 調用 AI 生成 Mermaid code
        mermaid_code, usage_info = ai_service.generate_content(prompt)
        
        # 清理 mermaid code
        clean_code = mermaid_code.strip()
        if clean_code.startswith("```mermaid"):
            clean_code = clean_code[len("```mermaid"):].strip()
        if clean_code.startswith("```"):
            clean_code = clean_code[3:].strip()
        if clean_code.endswith("```"):
            clean_code = clean_code[:-3].strip()
        
        return jsonify({
            "success": True,
            "mermaid_code": clean_code,
            "usage": usage_info
        })
        
    except Exception as e:
        current_app.logger.error(f"生成 Mermaid code 失敗: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route('/api/generate-flowchart', methods=['POST'])
def generate_flowchart():
    """將 Mermaid code 轉換為 PNG 流程圖"""
    try:
        data = request.json
        mermaid_code = data.get('mermaid_code', '').strip()
        
        if not mermaid_code:
            return jsonify({"success": False, "error": "Mermaid code 不能為空"}), 400
        
        # 獲取 Kroki 服務
        kroki_service = get_kroki_service()
        
        # 生成流程圖
        result = kroki_service.generate_flowchart(mermaid_code)
        
        if result['success']:
            return jsonify({
                "success": True,
                "filename": result['filename'],
                "download_url": f"/api/download/{result['filename']}"
            })
        else:
            return jsonify({
                "success": False,
                "error": result['error']
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"生成流程圖失敗: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route('/api/generate-flowchart-full', methods=['POST'])
def generate_flowchart_full():
    """完整流程：從描述直接生成 PNG 流程圖"""
    try:
        data = request.json
        description = data.get('description', '').strip()
        
        if not description:
            return jsonify({"success": False, "error": "流程描述不能為空"}), 400
        
        # 獲取服務
        ai_service = get_ai_service()
        kroki_service = get_kroki_service()
        
        # 1. 生成 Mermaid code
        prompt = kroki_service.generate_mermaid_prompt(description)
        mermaid_code, usage_info = ai_service.generate_content(prompt)
        
        # 清理 mermaid code
        clean_code = mermaid_code.strip()
        if clean_code.startswith("```mermaid"):
            clean_code = clean_code[len("```mermaid"):].strip()
        if clean_code.startswith("```"):
            clean_code = clean_code[3:].strip()
        if clean_code.endswith("```"):
            clean_code = clean_code[:-3].strip()
        
        # 2. 轉換為 PNG
        result = kroki_service.generate_flowchart(clean_code)
        
        if result['success']:
            return jsonify({
                "success": True,
                "mermaid_code": clean_code,
                "filename": result['filename'],
                "download_url": f"/api/download/{result['filename']}",
                "usage": usage_info
            })
        else:
            return jsonify({
                "success": False,
                "mermaid_code": clean_code,
                "error": result['error']
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"生成流程圖失敗: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

