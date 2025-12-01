import re

# 讀取 HTML 文件
with open('templates/index_v3_daisy.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 修復轉義的單引號問題
# 將 switchTab(\\'help\\', event) 改為 switchTab('help', event)
content = content.replace("switchTab(\\'help\\', event)", "switchTab('help', event)")

# 寫回文件
with open('templates/index_v3_daisy.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("HTML 文件修復完成!")
