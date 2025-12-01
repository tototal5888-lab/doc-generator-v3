import re

# 讀取 HTML 文件
with open('templates/index_v3_daisy.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 在 tabs 區域添加 HELP 按鈕
tabs_pattern = r'(<button class="tab" onclick="switchTab\(\'config\', event\)">[\s\S]*?</button>)\s*(</div>)'
tabs_replacement = r'\1\n            <button class="tab" onclick="switchTab(\'help\', event)">\n                <span>❓</span> 使用說明\n            </button>\n        \2'
content = re.sub(tabs_pattern, tabs_replacement, content, count=1)

# 2. 在 config-tab 後添加 help-tab 內容區域
config_tab_end = r'(</div>\s*</div>\s*</div>\s*</div>\s*<!-- 模板檢視模態框 -->)'
help_tab_html = '''
            <!-- 使用說明 Tab -->
            <div id="help-tab" class="tab-content full-width">
                <div class="card">
                    <div class="card-header">
                        <span class="card-icon">❓</span>
                        <h2 class="card-title">系統架構說明</h2>
                    </div>
                    <div id="help-content" style="padding: 20px; max-height: 70vh; overflow-y: auto; line-height: 1.6;">
                        <div style="text-align: center; padding: 40px; color: #94a3b8;">
                            <div style="font-size: 3rem; margin-bottom: 15px;">📖</div>
                            <div>載入中...</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- 模板檢視模態框 -->'''
content = re.sub(config_tab_end, help_tab_html, content, count=1)

# 3. 在 JavaScript 引入區域添加 help.js
js_pattern = r'(<script src="/static/js/generate\.js"></script>)'
js_replacement = r'\1\n    <script src="/static/js/help.js"></script>'
content = re.sub(js_pattern, js_replacement, content, count=1)

# 寫回文件
with open('templates/index_v3_daisy.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("HTML 文件修改完成!")
