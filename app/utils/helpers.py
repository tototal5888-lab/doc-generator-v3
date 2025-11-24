import os
from datetime import datetime

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
