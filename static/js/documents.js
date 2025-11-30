// ==================== 文檔記錄相關 ====================

let allDocuments = [];
let currentFilter = 'all';

/**
 * 載入已生成的文檔
 */
async function loadGeneratedDocuments() {
    try {
        const response = await fetch(`${API_BASE_URL}/generated_documents`);
        allDocuments = await response.json();
        filterDocuments(currentFilter);
    } catch (error) {
        console.error('載入文檔列表失敗:', error);
    }
}

/**
 * 篩選文檔
 * @param {string} filterType - 'all', 'generated', 'optimized'
 */
function filterDocuments(filterType) {
    currentFilter = filterType;
    let filteredDocs = [];

    if (filterType === 'all') {
        filteredDocs = allDocuments;
    } else if (filterType === 'optimized') {
        // 優化簡報：檔名包含 _v數字.pptx
        filteredDocs = allDocuments.filter(doc => /_v\d+\.pptx$/i.test(doc.filename));
    } else if (filterType === 'generated') {
        // 生成文檔：排除優化簡報
        filteredDocs = allDocuments.filter(doc => !/_v\d+\.pptx$/i.test(doc.filename));
    }

    renderDocumentList(filteredDocs);
}

/**
 * 渲染文檔列表
 * @param {Array} documents - 文檔列表
 */
function renderDocumentList(documents) {
    const listElement = document.getElementById('document-list');
    const formatIcons = {
        'DOCX': '📄',
        'PPTX': '📊',
        'PDF': '📕',
        'MD': '📝'
    };

    if (documents.length === 0) {
        listElement.innerHTML = '<div style="text-align: center; padding: 40px; color: #94a3b8;">暫無符合條件的文檔</div>';
    } else {
        listElement.innerHTML = documents.map(doc => `
            <div class="list-item">
                <input type="checkbox" class="doc-checkbox" value="${doc.filename}" onchange="updateBatchDeleteButton()" style="margin-right: 12px;">
                <div class="list-item-info">
                    <div class="list-item-name">
                        ${formatIcons[doc.format] || '📄'} ${doc.filename}
                    </div>
                    <div class="list-item-meta">
                        <span>📦 ${formatFileSize(doc.size)}</span>
                        <span>📅 ${doc.created}</span>
                        <span class="badge badge-primary">${doc.format}</span>
                    </div>
                </div>
                <div style="display: flex; gap: 8px;">
                    <a href="${API_BASE_URL}/download/${doc.filename}" class="btn btn-success btn-sm">
                        ⬇️ 下載
                    </a>
                    <button onclick="deleteGeneratedDocument('${doc.filename}')" class="btn btn-danger btn-sm">
                        🗑️ 刪除
                    </button>
                </div>
            </div>
        `).join('');
    }

    // 重置批量刪除按鈕狀態
    updateBatchDeleteButton();
}

/**
 * 刪除生成的文檔
 * @param {string} filename - 文檔檔名
 */
async function deleteGeneratedDocument(filename) {
    if (!confirm(`確定要刪除文檔 "${filename}" 嗎？`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/delete_generated/${filename}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            loadGeneratedDocuments();
        } else {
            alert('❌ ' + (data.error || '刪除失敗'));
        }
    } catch (error) {
        alert('❌ 刪除失敗: ' + error.message);
    }
}

/**
 * 全選/取消全選
 */
function toggleSelectAll() {
    const selectAllCheckbox = document.getElementById('select-all-docs');
    const checkboxes = document.querySelectorAll('.doc-checkbox');
    checkboxes.forEach(cb => cb.checked = selectAllCheckbox.checked);
    updateBatchDeleteButton();
}

/**
 * 更新批量刪除按鈕顯示狀態
 */
function updateBatchDeleteButton() {
    const checkboxes = document.querySelectorAll('.doc-checkbox:checked');
    const batchDeleteBtn = document.getElementById('batch-delete-btn');
    const selectAllCheckbox = document.getElementById('select-all-docs');

    if (checkboxes.length > 0) {
        batchDeleteBtn.style.display = 'block';
        batchDeleteBtn.textContent = `🗑️ 刪除選中項 (${checkboxes.length})`;
    } else {
        batchDeleteBtn.style.display = 'none';
    }

    // 更新全選框狀態
    const allCheckboxes = document.querySelectorAll('.doc-checkbox');
    selectAllCheckbox.checked = allCheckboxes.length > 0 && checkboxes.length === allCheckboxes.length;
}

/**
 * 批量刪除文檔
 */
async function batchDeleteDocuments() {
    const checkboxes = document.querySelectorAll('.doc-checkbox:checked');
    const filenames = Array.from(checkboxes).map(cb => cb.value);

    if (filenames.length === 0) {
        alert('⚠️ 請先選擇要刪除的文檔');
        return;
    }

    if (!confirm(`確定要刪除 ${filenames.length} 個文檔嗎？`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/batch_delete_generated`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filenames: filenames })
        });

        const data = await response.json();

        if (data.success) {
            document.getElementById('select-all-docs').checked = false;
            loadGeneratedDocuments();
        } else {
            alert('❌ ' + (data.error || '批量刪除失敗'));
        }
    } catch (error) {
        alert('❌ 批量刪除失敗: ' + error.message);
    }
}
