/**
 * 流程圖生成模組 - 使用 AI 生成 Mermaid code 並透過 Kroki 轉換為 PNG
 */

// 生成 Mermaid Code（透過 AI）
async function generateMermaidCode() {
    const description = document.getElementById('flowchart-description').value.trim();

    if (!description) {
        showFlowchartAlert('error', '❌ 請輸入流程描述');
        return;
    }

    // 顯示載入狀態
    const btn = document.getElementById('generate-mermaid-btn');
    const textSpan = document.getElementById('generate-mermaid-text');
    const loadingSpan = document.getElementById('generate-mermaid-loading');

    btn.disabled = true;
    textSpan.classList.add('hidden');
    loadingSpan.classList.remove('hidden');

    try {
        const response = await fetch(`${API_BASE_URL}/generate-mermaid`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ description })
        });

        const result = await response.json();

        if (result.success) {
            document.getElementById('mermaid-code').value = result.mermaid_code;
            showFlowchartAlert('success', '✅ Mermaid Code 生成成功！');
        } else {
            showFlowchartAlert('error', '❌ 生成失敗: ' + (result.error || '未知錯誤'));
        }
    } catch (error) {
        showFlowchartAlert('error', '❌ 請求失敗: ' + error.message);
    } finally {
        btn.disabled = false;
        textSpan.classList.remove('hidden');
        loadingSpan.classList.add('hidden');
    }
}

// 生成 PNG 流程圖（透過 Kroki）
async function generateFlowchartPNG() {
    const mermaidCode = document.getElementById('mermaid-code').value.trim();

    if (!mermaidCode) {
        showFlowchartAlert('error', '❌ 請先生成或輸入 Mermaid Code');
        return;
    }

    // 顯示載入狀態
    const btn = document.getElementById('generate-png-btn');
    const textSpan = document.getElementById('generate-png-text');
    const loadingSpan = document.getElementById('generate-png-loading');

    btn.disabled = true;
    textSpan.classList.add('hidden');
    loadingSpan.classList.remove('hidden');

    try {
        const response = await fetch(`${API_BASE_URL}/generate-flowchart`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mermaid_code: mermaidCode })
        });

        const result = await response.json();

        if (result.success) {
            // 顯示圖片預覽
            const previewDiv = document.getElementById('flowchart-preview');
            previewDiv.innerHTML = `<img src="${result.download_url}" alt="流程圖" class="max-w-full rounded-lg shadow-lg">`;

            // 顯示下載按鈕
            const downloadDiv = document.getElementById('flowchart-download');
            const downloadLink = document.getElementById('flowchart-download-link');
            downloadLink.href = result.download_url;
            downloadLink.download = result.filename;
            downloadDiv.classList.remove('hidden');

            showFlowchartAlert('success', '✅ 流程圖生成成功！');
        } else {
            showFlowchartAlert('error', '❌ 生成失敗: ' + (result.error || '未知錯誤'));
        }
    } catch (error) {
        showFlowchartAlert('error', '❌ 請求失敗: ' + error.message);
    } finally {
        btn.disabled = false;
        textSpan.classList.remove('hidden');
        loadingSpan.classList.add('hidden');
    }
}

// 顯示流程圖提示訊息
function showFlowchartAlert(type, message) {
    const alertDiv = document.getElementById('flowchart-alert');
    alertDiv.className = `alert ${type === 'success' ? 'alert-success' : 'alert-error'} mb-4`;
    alertDiv.innerHTML = `<span>${message}</span>`;
    alertDiv.classList.remove('hidden');

    // 5秒後自動隱藏
    setTimeout(() => {
        alertDiv.classList.add('hidden');
    }, 5000);
}

// 清空流程圖表單
function clearFlowchartForm() {
    document.getElementById('flowchart-description').value = '';
    document.getElementById('mermaid-code').value = '';
    document.getElementById('flowchart-preview').innerHTML = `
        <span class="text-6xl opacity-50">📊</span>
        <p class="mt-4 opacity-70">流程圖將顯示在這裡</p>
    `;
    document.getElementById('flowchart-download').classList.add('hidden');
    document.getElementById('flowchart-alert').classList.add('hidden');
}
