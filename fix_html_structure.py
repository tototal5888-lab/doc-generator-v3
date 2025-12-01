import re

# 讀取 HTML 文件
with open('templates/index_v3_daisy.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 修復 HTML 結構 - 在 help-tab 之前添加缺失的閉合標籤
# 找到 save-config-btn 後面的位置,添加正確的閉合標籤
pattern = r'(<button id="save-config-btn"[^>]*>[\s\S]*?</button>)\s*(\r?\n\s*)(<!-- 使用說明 Tab -->)'
replacement = r'\1\n                </div>\n            </div>\n\n            \3'

content = re.sub(pattern, replacement, content, count=1)

# 寫回文件
with open('templates/index_v3_daisy.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("HTML 結構修復完成!")
