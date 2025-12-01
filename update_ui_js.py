import re

# 讀取 ui.js 文件
with open('static/js/ui.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 在 switchTab 函數中添加 help 處理
# 找到 optimize 處理的位置,在它之前插入 help 處理
pattern = r"(if \(tabName === 'generate'\) loadTemplateOptions\(\);)\s*(if \(tabName === 'optimize'\))"
replacement = r"\1\n    if (tabName === 'help') {\n        if (typeof loadHelpContent === 'function') {\n            loadHelpContent();\n        }\n    }\n    \2"

content = re.sub(pattern, replacement, content, count=1)

# 寫回文件
with open('static/js/ui.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("ui.js 文件修改完成!")
