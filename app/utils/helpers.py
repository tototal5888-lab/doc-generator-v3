import os
import re
from datetime import datetime
from werkzeug.utils import secure_filename

def log_cost_to_file(model, input_tokens, output_tokens, cost):
    """記錄成本到文件"""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    log_file = os.path.join(log_dir, 'cost_log.csv')
    
    # 如果文件不存在，寫入表頭
    if not os.path.exists(log_file):
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("Timestamp,Model,Input Tokens,Output Tokens,Cost (USD)\n")
            
    # 追加記錄
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp},{model},{input_tokens},{output_tokens},{cost:.6f}\n")

def safe_filename(filename):
    """
    安全的文件名處理，支持中文
    保留中文、字母、數字、下劃線、點、減號
    """
    # 如果文件名為空，返回默認名
    if not filename:
        return "unnamed_file"
        
    # 分離擴展名
    name, ext = os.path.splitext(filename)
    
    # 移除非法字符，只保留中文、字母、數字、下劃線、點、減號
    # \u4e00-\u9fa5 是中文字符範圍
    cleaned_name = re.sub(r'[^\w\u4e00-\u9fa5\-\.]', '_', name)
    
    # 如果清理後為空，使用時間戳
    if not cleaned_name:
        cleaned_name = datetime.now().strftime("%Y%m%d%H%M%S")
        
    return cleaned_name + ext
