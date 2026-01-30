import os

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
