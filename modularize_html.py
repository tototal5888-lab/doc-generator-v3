"""
HTML 模塊化拆分腳本
自動將 index_v3.html 中的 CSS 和 JavaScript 提取到獨立文件
"""
import re
import os

# 讀取原始 HTML
with open('templates/index_v3.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# ==================== Phase 1: 提取 CSS ====================
print("Phase 1: 提取 CSS...")

# 提取 <style> 標籤中的所有 CSS
style_match = re.search(r'<style>(.*?)</style>', html_content, re.DOTALL)
if style_match:
    full_css = style_match.group(1).strip()
    
    # 分離不同類型的 CSS
    # 1. main.css: 基礎樣式、變量、全局樣式
    main_css_parts = []
    
    # 提取變量和基礎樣式
    main_css_parts.append(re.search(r'\* \{.*?\}', full_css, re.DOTALL).group(0))
    main_css_parts.append(re.search(r':root \{.*?\}', full_css, re.DOTALL).group(0))
    main_css_parts.append(re.search(r'body \{.*?\}', full_css, re.DOTALL).group(0))
    main_css_parts.append(re.search(r'\.container \{.*?\}', full_css, re.DOTALL).group(0))
    main_css_parts.append(re.search(r'\.header \{.*?\}', full_css, re.DOTALL).group(0))
    main_css_parts.append(re.search(r'\.header h1 \{.*?\}', full_css, re.DOTALL).group(0))
    main_css_parts.append(re.search(r'\.header-icon \{.*?\}', full_css, re.DOTALL).group(0))
    main_css_parts.append(re.search(r'\.header \.version \{.*?\}', full_css, re.DOTALL).group(0))
    main_css_parts.append(re.search(r'\.main-content \{.*?\}', full_css, re.DOTALL).group(0))
    
    # 2. components.css: 組件樣式
    components_patterns = [
        r'\.card.*?\}',
        r'\.form-.*?\}',
        r'\.format-.*?\}',
        r'\.upload-.*?\}',
        r'\.btn.*?\}',
        r'\.tab.*?\}',
        r'\.list-.*?\}',
        r'\.alert.*?\}',
        r'\.spinner.*?\}',
        r'\.badge.*?\}',
        r'\.modal.*?\}',
        r'\.result-.*?\}',
        r'::-webkit-scrollbar.*?\}'
    ]
    
    components_css_parts = []
    for pattern in components_patterns:
        matches = re.finditer(pattern, full_css, re.DOTALL)
        for match in matches:
            components_css_parts.append(match.group(0))
    
    # 3. animations.css: 動畫
    animations_css = re.search(r'/\* 動畫 \*/(.*?)(?=/\* 模態框樣式 \*/|$)', full_css, re.DOTALL)
    if animations_css:
        animations_css_content = animations_css.group(0)
    else:
        # 手動提取動畫
        animations_css_content = """/* 動畫 */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fadeInDown {
    from {
        opacity: 0;
        transform: translateY(-30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes slideInDown {
    from {
        transform: translateY(-20px);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

@keyframes spin {
    to { transform: rotate(360deg); }
}
"""
    
    # 創建 CSS 目錄
    os.makedirs('static/css', exist_ok=True)
    
    # 保存 main.css
    with open('static/css/main.css', 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(main_css_parts))
    print("✅ 已創建 static/css/main.css")
    
    # 保存 components.css
    with open('static/css/components.css', 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(set(components_css_parts)))  # 使用 set 去重
    print("✅ 已創建 static/css/components.css")
    
    # 保存 animations.css
    with open('static/css/animations.css', 'w', encoding='utf-8') as f:
        f.write(animations_css_content)
    print("✅ 已創建 static/css/animations.css")

# ==================== Phase 2: 提取 JavaScript ====================
print("\nPhase 2: 提取 JavaScript...")

# 提取 <script> 標籤中的所有 JavaScript
script_match = re.search(r'<script>(.*?)</script>', html_content, re.DOTALL)
if script_match:
    full_js = script_match.group(1).strip()
    
    # 創建 JS 目錄
    os.makedirs('static/js', exist_ok=True)
    
    # 1. api.js: API 相關函數
    api_js = f"""// API 基礎配置
const API_BASE_URL = 'http://127.0.0.1:5000/api';

// 顯示提示訊息
function showAlert(elementId, type, message) {{
    const alertElement = document.getElementById(elementId);
    if (!alertElement) return;
    
    alertElement.className = `alert alert-${{type}} show`;
    alertElement.textContent = message;
    
    setTimeout(() => {{
        alertElement.classList.remove('show');
    }}, 5000);
}}
"""
    
    with open('static/js/api.js', 'w', encoding='utf-8') as f:
        f.write(api_js)
    print("✅ 已創建 static/js/api.js")
    
    # 2. ui.js: UI 交互函數
    # 提取 switchTab, clearForm 等函數
    ui_functions = []
    for func_name in ['switchTab', 'clearForm', 'updateModelOptions']:
        func_match = re.search(rf'function {func_name}\(.*?\{{.*?^\s*\}}', full_js, re.DOTALL | re.MULTILINE)
        if func_match:
            ui_functions.append(func_match.group(0))
    
    with open('static/js/ui.js', 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(ui_functions))
    print("✅ 已創建 static/js/ui.js")
    
    # 3-5. 其他 JS 文件暫時創建空文件
    for js_file in ['doc-types.js', 'templates.js', 'documents.js']:
        with open(f'static/js/{js_file}', 'w', encoding='utf-8') as f:
            f.write(f'// {js_file} - 待實現\n')
        print(f"✅ 已創建 static/js/{js_file}")

# ==================== Phase 3: 修改 HTML ====================
print("\nPhase 3: 修改 HTML...")

# 移除 <style> 標籤
html_content = re.sub(r'<style>.*?</style>', '', html_content, flags=re.DOTALL)

# 在 </head> 前添加 CSS 引用
css_links = '''
    <!-- 模塊化 CSS -->
    <link rel="stylesheet" href="/static/css/main.css">
    <link rel="stylesheet" href="/static/css/components.css">
    <link rel="stylesheet" href="/static/css/animations.css">
</head>'''

html_content = html_content.replace('</head>', css_links)

# 移除 <script> 標籤內容，保留標籤結構
html_content = re.sub(r'<script>(.*?)</script>', '<script src="/static/js/api.js"></script>\n    <script src="/static/js/ui.js"></script>\n    <script src="/static/js/doc-types.js"></script>\n    <script src="/static/js/templates.js"></script>\n    <script src="/static/js/documents.js"></script>', html_content, flags=re.DOTALL)

# 保存修改後的 HTML
with open('templates/index_v3_modular.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("✅ 已創建 templates/index_v3_modular.html")

print("\n" + "="*50)
print("模塊化完成！")
print("="*50)
print("\n文件統計：")
print(f"  原始 HTML: {len(open('templates/index_v3.html', 'r', encoding='utf-8').readlines())} 行")
print(f"  新 HTML: {len(open('templates/index_v3_modular.html', 'r', encoding='utf-8').readlines())} 行")
print("\n創建的文件：")
print("  - static/css/main.css")
print("  - static/css/components.css")
print("  - static/css/animations.css")
print("  - static/js/api.js")
print("  - static/js/ui.js")
print("  - static/js/doc-types.js")
print("  - static/js/templates.js")
print("  - static/js/documents.js")
print("  - templates/index_v3_modular.html")
print("\n注意：JavaScript 文件需要手動完善功能")
