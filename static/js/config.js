// ==================== 模型配置相關 ====================

/**
 * 載入模型配置
 */
async function loadConfig() {
    try {
        const response = await fetch(`${API_BASE_URL}/config`);
        const config = await response.json();

        document.getElementById('api-type').value = config.api_type || 'gemini';
        document.getElementById('openai-model').value = config.openai_model || 'gpt-4o-mini';

        // 根據選擇的 API 類型更新顯示
        updateModelOptions();
    } catch (error) {
        console.error('載入配置失敗:', error);
    }
}

/**
 * 保存模型配置
 */
async function saveModelConfig() {
    const config = {
        api_type: document.getElementById('api-type').value,
        openai_model: document.getElementById('openai-model').value
    };

    try {
        const response = await fetch(`${API_BASE_URL}/config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });

        const result = await response.json();
        if (result.success) {
            showAlert('config-alert', 'success', '✅ 模型設定已保存');
        } else {
            showAlert('config-alert', 'error', '❌ 保存失敗: ' + (result.error || '未知錯誤'));
        }
    } catch (error) {
        showAlert('config-alert', 'error', '❌ 保存失敗: ' + error.message);
    }
}
