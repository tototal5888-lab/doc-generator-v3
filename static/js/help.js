// HELP 功能處理
async function loadHelpContent() {
    const contentDiv = document.getElementById('help-content');
    if (!contentDiv) return;

    try {
        const response = await fetch('/api/help');
        const data = await response.json();

        if (data.success) {
            // 將 Markdown 內容轉換為 HTML 格式顯示
            const content = data.content
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/\n/g, '<br>');

            contentDiv.innerHTML = `<pre style="white-space: pre-wrap; font-family: 'Inter', sans-serif; line-height: 1.8;">${content}</pre>`;
        } else {
            contentDiv.innerHTML = '<div class="alert alert-error">載入失敗: ' + (data.error || '未知錯誤') + '</div>';
        }
    } catch (error) {
        console.error('載入幫助文檔失敗:', error);
        contentDiv.innerHTML = '<div class="alert alert-error">載入失敗,請稍後再試</div>';
    }
}
