// ==================== UI 交互函數 ====================

/**
 * Tab 切換
 * @param {string} tabName - Tab 名稱
 * @param {Event} event - 事件對象
 */
function switchTab(tabName, event) {
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    if (event && event.target) event.target.closest('.tab').classList.add('active');
    document.getElementById(tabName + '-tab').classList.add('active');

    if (tabName === 'templates') loadTemplates();
    if (tabName === 'documents') loadGeneratedDocuments();
    if (tabName === 'config') loadConfig();
    if (tabName === 'generate') loadTemplateOptions();
}

/**
 * 清空表單
 */
function clearForm() {
    document.getElementById('doc-type').value = '';
    document.getElementById('template-select').value = '';
    document.getElementById('requirements').value = '';
    document.querySelectorAll('input[name="format"]').forEach(input => {
        input.checked = input.value === 'docx';
    });
    document.getElementById('result-section').style.display = 'none';
    document.getElementById('no-result').style.display = 'block';

    // 清空 AI 優化相關內容
    document.getElementById('optimized-requirements').value = '';
    document.getElementById('optimized-section').style.display = 'none';
    if (typeof originalRequirements !== 'undefined') {
        originalRequirements = '';
    }

    // 重置文檔類型相關 UI
    document.getElementById('requirements-label').textContent = '需求描述';
    document.getElementById('requirements').placeholder = '請描述您的具體需求...';
    document.getElementById('old-doc-upload-section').style.display = 'none';
    window.extractedImageFolder = null;
}

/**
 * 更新模型選項顯示
 */
function updateModelOptions() {
    const apiType = document.getElementById('api-type').value;
    const openaiModelGroup = document.getElementById('openai-model-group');
    const apiTypeHint = document.getElementById('api-type-hint');

    if (apiType === 'openai') {
        openaiModelGroup.style.display = 'block';
        apiTypeHint.textContent = '使用 OpenAI GPT 模型,需要有效的 API Key';
    } else if (apiType === 'gemini') {
        openaiModelGroup.style.display = 'none';
        apiTypeHint.textContent = '使用 Google Gemini 2.0 Flash,免費額度高';
    } else if (apiType === 'mock') {
        openaiModelGroup.style.display = 'none';
        apiTypeHint.textContent = '模擬模式,不調用真實 API,用於測試';
    }
}