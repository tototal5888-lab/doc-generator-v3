// ==================== 模板管理相關 ====================

/**
 * 上傳模板
 */
async function uploadTemplate() {
    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];

    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE_URL}/upload_template`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            showAlert('upload-alert', 'success', '✅ ' + result.message);
            loadTemplates();
            loadTemplateOptions();
        } else {
            showAlert('upload-alert', 'error', '❌ ' + result.error);
        }
    } catch (error) {
        showAlert('upload-alert', 'error', '❌ 上傳失敗: ' + error.message);
    }

    fileInput.value = '';
}

/**
 * 載入模板列表
 */
async function loadTemplates() {
    try {
        const response = await fetch(`${API_BASE_URL}/templates`);
        const templates = await response.json();

        const listElement = document.getElementById('template-list');

        if (templates.length === 0) {
            listElement.innerHTML = '<div style="text-align: center; padding: 40px; color: #94a3b8;">尚無模板</div>';
        } else {
            listElement.innerHTML = templates.map(template => `
                <div class="list-item">
                    <div class="list-item-info">
                        <div class="list-item-name">
                            <span class="badge badge-primary">${template.type}</span>
                            ${template.filename}
                        </div>
                        <div class="list-item-meta">
                            <span>📦 ${formatFileSize(template.size)}</span>
                            <span>📅 ${template.modified}</span>
                        </div>
                    </div>
                    <div style="display: flex; gap: 8px;">
                        <a href="${API_BASE_URL}/download_template/${encodeURIComponent(template.filename)}" 
                           class="btn btn-secondary btn-sm" 
                           download="${template.filename}">
                            📥 下載
                        </a>
                        <button class="btn btn-danger btn-sm" onclick="deleteTemplate('${template.filename}', event)">
                            🗑️ 刪除
                        </button>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('載入模板失敗:', error);
    }
}

/**
 * 載入模板選項
 */
async function loadTemplateOptions() {
    try {
        const response = await fetch(`${API_BASE_URL}/templates`);
        const templates = await response.json();

        const selectElement = document.getElementById('template-select');

        if (templates.length === 0) {
            selectElement.innerHTML = '<option value="">請先上傳模板...</option>';
        } else {
            selectElement.innerHTML = '<option value="">請選擇模板...</option>' +
                templates.map((template, index) =>
                    `<option value="${template.filename}">${index + 1}. [${template.type}] ${template.filename}</option>`
                ).join('');
        }
    } catch (error) {
        console.error('載入模板選項失敗:', error);
    }
}

/**
 * 檢視模板內容
 * @param {string} filename - 模板檔名
 * @param {Event} event - 事件對象
 */
async function viewTemplate(filename, event) {
    event.stopPropagation();

    const modal = document.getElementById('template-modal');
    const modalTitle = document.getElementById('modal-template-name');
    const modalContent = document.getElementById('modal-template-content');

    // 顯示模態框
    modal.classList.add('show');
    modalTitle.textContent = `模板內容: ${filename}`;
    modalContent.textContent = '載入中...';

    try {
        const response = await fetch(`${API_BASE_URL}/view_template/${encodeURIComponent(filename)}`);
        const result = await response.json();

        if (result.success) {
            modalContent.textContent = result.content;
        } else {
            modalContent.textContent = `錯誤: ${result.error}`;
        }
    } catch (error) {
        modalContent.textContent = `載入失敗: ${error.message}`;
    }
}

/**
 * 關閉模板檢視模態框
 */
function closeTemplateModal() {
    const modal = document.getElementById('template-modal');
    modal.classList.remove('show');
}

/**
 * 刪除模板
 * @param {string} filename - 模板檔名
 * @param {Event} event - 事件對象
 */
async function deleteTemplate(filename, event) {
    event.stopPropagation();

    if (!confirm(`確定要刪除模板 "${filename}" 嗎？`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/delete_template/${filename}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            loadTemplates();
            loadTemplateOptions();
        } else {
            alert('❌ ' + (data.error || '刪除失敗'));
        }
    } catch (error) {
        alert('❌ 刪除失敗: ' + error.message);
    }
}

// ==================== 拖放上傳事件處理 ====================

// 頁面載入時初始化拖放上傳
window.addEventListener('DOMContentLoaded', () => {
    const uploadArea = document.getElementById('upload-area');

    if (uploadArea) {
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');

            const file = e.dataTransfer.files[0];
            const fileInput = document.getElementById('file-input');
            fileInput.files = e.dataTransfer.files;
            uploadTemplate();
        });
    }

    // 點擊模態框外部關閉
    document.addEventListener('click', function (event) {
        const modal = document.getElementById('template-modal');
        if (event.target === modal) {
            closeTemplateModal();
        }
    });

    // ESC 鍵關閉模態框
    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') {
            closeTemplateModal();
        }
    });
});
