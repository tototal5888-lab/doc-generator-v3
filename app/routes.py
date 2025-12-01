import os
import json
import time
from flask import Blueprint, render_template, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
from .utils.helpers import safe_filename
from .services import FileProcessor, FormatConverter, AIService

bp = Blueprint('main', __name__)

# 初始化服務 (在首次請求時或應用啟動時)
# 由於 Blueprint 在應用創建前定義，我們這裡使用延遲初始化或在視圖函數中獲取配置
# 為了簡單起見，我們在視圖函數中實例化 AIService，或者在 app context 中存儲

def get_ai_service():
    if not hasattr(current_app, 'ai_service'):
        current_app.ai_service = AIService(current_app.config)
    return current_app.ai_service

@bp.route('/')
def index():
    return render_template('index_v3_daisy.html')

@bp.route('/help')
def help_page():
    return render_template('help.html')

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

        # 根據文檔類型構建優化提示詞
        if doc_type == 'sop':
            # SOP 專用的優化提示詞
            role_def = "你現在是一位企業內部系統的 SOP 工程師，熟悉採購/廠商報價/審核流程。"
            if profile_content:
                role_def = "" # 使用 Profile 中的角色設定
            
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
            # 系統文檔的優化提示詞
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

        elif doc_type == 'technical_report':
            # 技術報告的優化提示詞
            optimize_prompt = f"""
{profile_content}
請優化以下技術報告的需求描述，使其更加清晰、完整、專業。

原始需求：
{requirements}

請提供優化後的需求描述，要求：
1. 補充背景資訊和問題陳述
2. 列出技術方案和分析方法
3. 包含數據分析和實施細節
4. 提供結論和建議
5. 使用專業術語，結構清晰
6. 使用 Markdown 格式輸出

優化後的需求描述："""

        else:
            # 預設的優化提示詞
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
            "tech_report": {
                "name": "技術報告",
                "prompt": f"""
{profile_content}
請根據以下模板結構和用戶需求，生成一份技術分析報告。

模板內容：
{template_content}

用戶需求：
{user_requirements}

要求：
1. 數據準確、分析深入
2. 包含背景、方法、結果、結論等部分
3. 圖表說明清晰
4. 技術細節完整
5. 根據模板格式調整輸出格式
6. 請生成完整的技術報告內容，使用Markdown格式輸出。
                """,
                "title": "技術分析報告"
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
            doc = FormatConverter.markdown_to_docx(generated_content, doc_config)
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
            
            prs = FormatConverter.markdown_to_pptx(generated_content, doc_config, image_folder_path)
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
        
        # 保存臨時文件
        filename = safe_filename(file.filename)
        temp_folder = current_app.config['UPLOAD_FOLDER']
        temp_path = os.path.join(temp_folder, f"temp_{filename}")
        file.save(temp_path)
        
        try:
            ext = filename.lower().split('.')[-1]
            content = ""
            image_info = None
            
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
            
            # 刪除臨時文件
            os.remove(temp_path)
            
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
            # 確保刪除臨時文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

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

