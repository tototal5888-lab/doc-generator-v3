import re

# 讀取 HTML 文件
with open('templates/index_v3_daisy.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到需要插入的位置
new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    
    # 1. 在 config 按鈕後添加 help 按鈕
    if "switchTab('config', event)" in line and '<button' in line:
        # 找到這個按鈕的結束標籤
        if i + 2 < len(lines) and '</button>' in lines[i + 2]:
            new_lines.append(lines[i + 1])  # 添加 icon 行
            new_lines.append(lines[i + 2])  # 添加 </button>
            # 添加 help 按鈕
            new_lines.append('            <button class="tab" onclick="switchTab(\'help\', event)">\n')
            new_lines.append('                <span>❓</span> 使用說明\n')
            new_lines.append('            </button>\n')
            # 跳過已經添加的兩行
            lines[i + 1] = ''
            lines[i + 2] = ''
    
    # 2. 在 config-tab 結束後添加 help-tab
    if '</div>' in line and i > 0:
        # 檢查是否是 config-tab 的結束
        prev_lines = ''.join(lines[max(0, i-10):i])
        if 'save-config-btn' in prev_lines and 'config-tab' in prev_lines:
            # 確認這是最後一個 </div>
            if i + 1 < len(lines) and '</div>' in lines[i + 1]:
                new_lines.append(lines[i + 1])  # 添加外層 </div>
                new_lines.append('\n')
                # 添加 help-tab
                new_lines.append('            <!-- 使用說明 Tab -->\n')
                new_lines.append('            <div id="help-tab" class="tab-content full-width">\n')
                new_lines.append('                <div class="card">\n')
                new_lines.append('                    <div class="card-header">\n')
                new_lines.append('                        <span class="card-icon">❓</span>\n')
                new_lines.append('                        <h2 class="card-title">系統架構說明</h2>\n')
                new_lines.append('                    </div>\n')
                new_lines.append('                    <div id="help-content" style="padding: 20px; max-height: 70vh; overflow-y: auto; line-height: 1.6;">\n')
                new_lines.append('                        <div style="text-align: center; padding: 40px; color: #94a3b8;">\n')
                new_lines.append('                            <div style="font-size: 3rem; margin-bottom: 15px;">📖</div>\n')
                new_lines.append('                            <div>載入中...</div>\n')
                new_lines.append('                        </div>\n')
                new_lines.append('                    </div>\n')
                new_lines.append('                </div>\n')
                new_lines.append('            </div>\n')
                lines[i + 1] = ''  # 跳過已添加的行
    
    # 3. 在 generate.js 後添加 help.js
    if '/static/js/generate.js' in line and '<script' in line:
        new_lines.append('    <script src="/static/js/help.js"></script>\n')

# 過濾空字符串
final_lines = [line for line in new_lines if line != '']

# 寫回文件
with open('templates/index_v3_daisy.html', 'w', encoding='utf-8') as f:
    f.writelines(final_lines)

print("HTML 文件重新生成完成!")
