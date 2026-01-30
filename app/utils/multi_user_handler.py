"""
多人員工作報告處理輔助函數
此檔案包含處理工作報告 Excel 多人員拆分的邏輯
"""

import os
import re
from datetime import datetime
from flask import current_app, jsonify
from app.services import FileProcessor, FormatConverter, AIService


def sanitize_filename(name):
    """清理檔名中的非法字元
    
    Args:
        name: 原始檔名
        
    Returns:
        str: 清理後的檔名
    """
    # 移除或替換檔名中不允許的字元
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    # 移除首尾空白
    name = name.strip()
    # 限制長度
    if len(name) > 50:
        name = name[:50]
    return name if name else 'unknown'


def generate_single_work_report(user_name, user_data, template_file, output_format, image_folder_name=None):
    """為單一人員生成工作報告
    
    Args:
        user_name: 人員名稱
        user_data: 該人員的資料文字
        template_file: 模板檔名
        output_format: 輸出格式 ('pptx' 或 'docx')
        image_folder_name: 圖片資料夾名稱
        
    Returns:
        dict: {'success': bool, 'filename': str, 'user': str}
    """
    try:
        # 1. 讀取模板
        template_path = os.path.join(current_app.config['TEMPLATE_STORAGE_FOLDER'], template_file)
        if not os.path.exists(template_path):
            return {'success': False, 'error': f'模板文件不存在: {template_file}'}
        
        template_content = FileProcessor.extract_text(template_path)
        
        # 2. 讀取 Profile (使用 SYS_PROFILE.md for work_report)
        profile_content = ""
        try:
            profile_path = 'SYS_PROFILE.md'
            if os.path.exists(profile_path):
                with open(profile_path, 'r', encoding='utf-8') as f:
                    profile_content = f.read()
                profile_content = f"{profile_content}\n\n=== Role Definition End ===\n\n"
        except Exception as e:
            print(f"[WARNING] Failed to read profile: {e}")
        
        # 3. 讀取 Prompt 模板（使用 utils.prompt_manager 避免循環依賴）
        try:
            from app.utils.prompt_manager import get_prompts_by_type
            _, generate_prompt_template = get_prompts_by_type('work_report')
        except ImportError as e:
            print(f"[ERROR] 無法導入 get_prompts_by_type: {e}")
            return {'success': False, 'error': '系統配置錯誤'}
        
        if not generate_prompt_template:
            return {'success': False, 'error': '無法載入工作報告 Prompt 配置'}
        
        # 4. 替換變數並構建 Prompt
        prompt = generate_prompt_template.replace('{user_requirements}', user_data)
        prompt = prompt.replace('{template_content}', template_content)
        full_prompt = profile_content + "\n\n" + prompt
        
        # 5. 調用 AI 生成內容
        ai_service = AIService(current_app.config)
        generated_content, usage_info = ai_service.generate_content(full_prompt)
        
        # 6. 格式轉換與保存
        datetime_str = datetime.now().strftime('%Y%m%d%H%M%S')
        safe_user_name = sanitize_filename(user_name)
        # 修改檔名格式：姓名在前
        base_filename = f"{safe_user_name}_generated_work_report_{datetime_str}"
        
        output_folder = current_app.config['OUTPUT_FOLDER']
        
        # 確定圖片資料夾路徑
        image_folder_path = None
        if image_folder_name:
            image_folder_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_folder_name)
        
        output_file_path = os.path.join(output_folder, f"{base_filename}.{output_format}")

        # 根據輸出格式生成文件
        if output_format == 'pptx':
            doc_config = {'title': f'{user_name}工作報告'}
            # 正確調用：content, doc_config, image_folder, template_path
            prs = FormatConverter.markdown_to_pptx(
                generated_content, 
                doc_config,
                image_folder_path,
                template_path
            )
            prs.save(output_file_path)
            output_file = output_file_path
            
        elif output_format == 'docx':
            doc_config = {'title': f'{user_name}工作報告'}
            doc = FormatConverter.markdown_to_docx(
                generated_content, 
                doc_config,
                template_path
            )
            doc.save(output_file_path)
            output_file = output_file_path
        else:
            return {'success': False, 'error': f'不支援的輸出格式: {output_format}'}
        
        if not os.path.exists(output_file):
            return {'success': False, 'error': '文件生成失敗'}
        
        # 7. 返回成功結果
        return {
            'success': True,
            'filename': os.path.basename(output_file),
            'user': user_name,
            'format': output_format
        }
        
    except Exception as e:
        print(f"[ERROR] 為 {user_name} 生成報告失敗: {e}")
        return {
            'success': False,
            'user': user_name,
            'error': str(e)
        }


def generate_multiple_work_reports(excel_data, template_file, output_format, image_folder_name=None):
    """為多個人員生成獨立的工作報告
    
    Args:
        excel_data: ExcelParser.parse_work_report_excel() 的返回值
        template_file: 模板檔名
        output_format: 輸出格式
        image_folder_name: 圖片資料夾名稱
        
    Returns:
        Response: JSON 回應
    """
    print(f"\n{'='*60}")
    print(f"[多人員處理] 開始處理多人員工作報告生成")
    print(f"{'='*60}")
    print(f"[多人員處理] 模板檔案: {template_file}")
    print(f"[多人員處理] 輸出格式: {output_format}")
    print(f"[多人員處理] 圖片資料夾: {image_folder_name}")
    print(f"[多人員處理] 人員數量: {len(excel_data.get('users', []))}")
    print(f"[多人員處理] 人員列表: {excel_data.get('users', [])}")
    
    try:
        results = []
        successful_files = []
        failed_users = []
        
        print(f"\n[多人員處理] 開始逐個處理人員...")
        
        # 為每個人員生成報告
        for idx, user_name in enumerate(excel_data['users'], 1):
            print(f"\n{'*'*60}")
            print(f"[多人員處理] 處理第 {idx}/{len(excel_data['users'])} 位人員: {user_name}")
            print(f"{'*'*60}")
            
            user_data = excel_data['data_by_user'].get(user_name, '')
            
            if not user_data:
                print(f"[多人員處理] ⚠️ {user_name}: 無資料")
                failed_users.append({'user': user_name, 'error': '無資料'})
                continue
            
            print(f"[多人員處理] {user_name}: 資料長度 = {len(user_data)} 字元")
            print(f"[多人員處理] {user_name}: 準備呼叫 generate_single_work_report...")
            
            try:
                result = generate_single_work_report(
                    user_name,
                    user_data,
                    template_file,
                    output_format,
                    image_folder_name
                )
                
                print(f"[多人員處理] {user_name}: generate_single_work_report 返回結果:")
                print(f"[多人員處理] {user_name}:   success = {result.get('success')}")
                print(f"[多人員處理] {user_name}:   filename = {result.get('filename')}")
                
                if result['success']:
                    print(f"[多人員處理] ✅ {user_name}: 生成成功")
                    successful_files.append({
                        'user': user_name,
                        'filename': result['filename'],
                        'format': result['format']
                    })
                else:
                    error_msg = result.get('error', '未知錯誤')
                    print(f"[多人員處理] ❌ {user_name}: 生成失敗 - {error_msg}")
                    failed_users.append({
                        'user': user_name,
                        'error': error_msg
                    })
            except Exception as e:
                error_msg = f"異常: {str(e)}"
                print(f"[多人員處理] ❌ {user_name}: 發生異常")
                print(f"[多人員處理] 異常訊息: {e}")
                import traceback
                traceback.print_exc()
                failed_users.append({
                    'user': user_name,
                    'error': error_msg
                })
        
        print(f"\n{'='*60}")
        print(f"[多人員處理] 所有人員處理完成")
        print(f"{'='*60}")
        print(f"[多人員處理] 成功: {len(successful_files)} 位")
        print(f"[多人員處理] 失敗: {len(failed_users)} 位")
        
        # 檢查是否有成功生成的檔案
        if not successful_files:
            print(f"[多人員處理] ❌ 所有人員的報告生成均失敗")
            return jsonify({
                'success': False,
                'error': '所有人員的報告生成均失敗',
                'details': failed_users
            }), 500
        
        print(f"[多人員處理] ✅ 準備返回成功回應")
        print(f"[多人員處理] 成功檔案列表:")
        for f in successful_files:
            print(f"[多人員處理]   - {f['user']}: {f['filename']}")
        
        # 返回多檔案結果
        response_data = {
            'success': True,
            'multiple': True,
            'files': successful_files,
            'count': len(successful_files),
            'failed': failed_users if failed_users else []
        }
        
        print(f"[多人員處理] 回應資料: {response_data}")
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"[多人員處理] ❌❌❌ 嚴重錯誤 ❌❌❌")
        print(f"{'='*60}")
        print(f"[多人員處理] 錯誤訊息: {e}")
        print(f"[多人員處理] 錯誤類型: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        print(f"{'='*60}")
        
        current_app.logger.error(f"多人員報告生成失敗: {e}")
        return jsonify({
            'success': False,
            'error': f'多人員報告生成失敗: {str(e)}'
        }), 500

