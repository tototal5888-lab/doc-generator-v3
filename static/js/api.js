// ==================== API 基礎配置 ====================
const API_BASE_URL = 'http://127.0.0.1:5000/api';

// ==================== 通用工具函數 ====================

/**
 * 顯示提示訊息
 * @param {string|HTMLElement} element - 元素 ID 或元素本身
 * @param {string} type - 類型: 'success' 或 'error'
 * @param {string} message - 訊息內容
 */
function showAlert(element, type, message) {
    const alertElement = typeof element === 'string' ? document.getElementById(element) : element;
    if (!alertElement) return;

    // 清除之前的類型
    alertElement.classList.remove('alert-success', 'alert-error', 'alert-warning', 'alert-info');

    // 添加新類型和顯示
    alertElement.classList.add(`alert-${type}`);
    alertElement.classList.remove('hidden');

    alertElement.textContent = message;

    // 5秒後自動隱藏
    setTimeout(() => {
        alertElement.classList.add('hidden');
    }, 5000);
}

/**
 * 格式化文件大小
 * @param {number} bytes - 文件大小(bytes)
 * @returns {string} 格式化後的文件大小
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}
