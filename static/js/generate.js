// ==================== 文檔生成相關 ====================

// 儲存原始需求
let originalRequirements = '';

/**
 * 生成文檔
 */
async function generateDocument() {
    const docType = document.getElementById('doc-type').value;
    const template = document.getElementById('template-select').value;
    const requirements = document.getElementById('requirements').value;
    const format = document.querySelector('input[name="format"]:checked').value;
    const alertElement = document.getElementById('generate-alert');
    const generateBtn = document.getElementById('generate-btn');

    if (!docType) {
        showAlert(alertElement, 'error', '❌ 請選擇文檔類型');
        return;
    }

    if (!template) {
        showAlert(alertElement, 'error', '❌ 請選擇模板');
        return;
    }

    generateBtn.innerHTML = '<span class="spinner"></span> 生成中...';
    generateBtn.disabled = true;

    try {
        const requestData = {
            doc_type: docType,
            template: template,
            requirements: requirements,
            output_format: format
        };

        // 如果有圖片文件夾，添加到請求中
        if (window.extractedImageFolder) {
            requestData.image_folder = window.extractedImageFolder;
        }

        const response = await fetch(`${API_BASE_URL}/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });

        const data = await response.json();

        if (data.success) {
            showAlert(alertElement, 'success', '✅ 文檔生成成功！');
            showGenerationResult(data);
            loadGeneratedDocuments();
        } else {
            showAlert(alertElement, 'error', '❌ ' + (data.error || '生成失敗'));
        }
    } catch (error) {
        showAlert(alertElement, 'error', '❌ 生成失敗: ' + error.message);
    } finally {
        generateBtn.innerHTML = '✨ 生成文檔';
        generateBtn.disabled = false;
    }
}

/**
 * 顯示生成結果
 * @param {Object} result - 生成結果
 */
function showGenerationResult(result) {
    document.getElementById('no-result').style.display = 'none';
    document.getElementById('result-section').style.display = 'block';

    const formatIcons = {
        'docx': '📄',
        'pptx': '📊',
        'pdf': '📕',
        'md': '📝'
    };

    const resultContent = document.getElementById('result-content');
    resultContent.innerHTML = `
        <div class="alert alert-success show">
            <div>
                <div style="font-size: 1.2rem; font-weight: 700; margin-bottom: 10px;">
                    ${formatIcons[result.format]} 文檔生成成功
                </div>
                <div style="margin-bottom: 15px;">
                    <strong>文件名:</strong> ${result.filename}<br>
                    <strong>模型:</strong> ${result.usage ? result.usage.model : 'Unknown'}<br>
                    <strong>消耗 Tokens:</strong> ${result.usage ? (result.usage.input_tokens + result.usage.output_tokens) : 0}<br>
                    <strong>預估成本:</strong> $${result.usage ? result.usage.cost.toFixed(4) : '0.0000'}
                </div>
                <a href="${API_BASE_URL}/download/${result.filename}" class="btn btn-success">
                    ⬇️ 下載文檔
                </a>
            </div>
        </div>
        <div style="margin-top: 25px;">
            <h4 style="margin-bottom: 15px; color: var(--dark);">📝 內容預覽</h4>
            <div class="result-preview">${result.preview || '無預覽內容'}</div>
        </div>
    `;
}

/**
 * 上傳舊文檔並提取內容
 */
async function uploadOldDocument() {
    const fileInput = document.getElementById('old-doc-input');
    const file = fileInput.files[0];

    if (!file) {
        alert('請先選擇文件');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    // 顯示處理中狀態
    const dropArea = document.getElementById('old-doc-drop-area');
    const originalHTML = dropArea.innerHTML;
    dropArea.innerHTML = '<div class="spinner"></div> 提取中...';

    try {
        const response = await fetch(`${API_BASE_URL}/extract_text`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            document.getElementById('requirements').value = data.content;

            // 如果有圖片信息，保存到全局變量
            if (data.images) {
                window.extractedImageFolder = data.images.folder;
                alert(`✅ 內容提取成功！共提取 ${data.images.count} 張圖片`);
            } else {
                window.extractedImageFolder = null;
                alert('✅ 內容提取成功！');
            }
        } else {
            alert('❌ ' + (data.error || '提取失敗'));
        }
    } catch (error) {
        alert('❌ 提取失敗: ' + error.message);
    } finally {
        // 恢復原始狀態
        dropArea.innerHTML = originalHTML;
    }
}

// ==================== AI 優化需求功能 ====================

/**
 * 優化需求
 */
async function optimizeRequirements() {
    const requirementsInput = document.getElementById('requirements');
    const requirements = requirementsInput.value.trim();
    const docType = document.getElementById('doc-type').value;

    if (!requirements) {
        alert('⚠️ 請先輸入需求描述');
        return;
    }

    if (!docType) {
        alert('⚠️ 請先選擇文檔類型');
        return;
    }

    // 儲存原始需求
    originalRequirements = requirements;

    // 顯示載入狀態
    const btn = document.getElementById('optimize-btn');
    const btnText = document.getElementById('optimize-btn-text');
    const btnLoading = document.getElementById('optimize-btn-loading');

    btn.disabled = true;
    btnText.style.display = 'none';
    btnLoading.style.display = 'inline';

    try {
        const response = await fetch('/api/optimize-requirements', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                requirements: requirements,
                doc_type: docType
            })
        });

        const data = await response.json();

        if (data.success) {
            // 顯示優化結果區域
            document.getElementById('optimized-section').style.display = 'block';
            document.getElementById('optimized-requirements').value = data.optimized_requirements;

            // 平滑滾動到優化結果
            document.getElementById('optimized-section').scrollIntoView({
                behavior: 'smooth',
                block: 'nearest'
            });
        } else {
            alert('❌ 優化失敗：' + (data.error || '未知錯誤'));
        }
    } catch (error) {
        console.error('優化需求失敗:', error);
        alert('❌ 優化失敗：' + error.message);
    } finally {
        // 恢復按鈕狀態
        btn.disabled = false;
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
    }
}

// ==================== 頁面初始化 ====================

// 頁面載入時初始化
window.addEventListener('DOMContentLoaded', () => {
    // 載入模板選項
    loadTemplateOptions();

    // 監聽文檔類型變更，動態調整 UI
    const docTypeSelect = document.getElementById('doc-type');
    const requirementsLabel = document.getElementById('requirements-label');
    const requirementsTextarea = document.getElementById('requirements');
    const oldDocUploadSection = document.getElementById('old-doc-upload-section');

    if (docTypeSelect) {
        docTypeSelect.addEventListener('change', function () {
            if (this.value === 'sop_optimize') {
                requirementsLabel.textContent = '舊 SOP 內容';
                requirementsTextarea.placeholder = '請在此貼上您想要優化的舊 SOP 文檔內容...\\n\\n或使用上方的「上傳舊文檔」功能自動提取內容';
                oldDocUploadSection.style.display = 'block';
            } else {
                requirementsLabel.textContent = '需求描述';
                requirementsTextarea.placeholder = '請描述您的具體需求...';
                oldDocUploadSection.style.display = 'none';
            }
        });
    }

    // 設置舊文檔拖曳功能
    const oldDocDropArea = document.getElementById('old-doc-drop-area');
    const oldDocInput = document.getElementById('old-doc-input');

    if (oldDocDropArea && oldDocInput) {
        // 點擊上傳區域時觸發文件選擇
        oldDocDropArea.addEventListener('click', function () {
            oldDocInput.click();
        });

        // 文件選擇後自動提取
        oldDocInput.addEventListener('change', function () {
            if (this.files.length > 0) {
                uploadOldDocument();
            }
        });

        // 防止預設拖曳行為
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            oldDocDropArea.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        // 拖曳時的視覺回饋
        ['dragenter', 'dragover'].forEach(eventName => {
            oldDocDropArea.addEventListener(eventName, function () {
                this.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            oldDocDropArea.addEventListener(eventName, function () {
                this.classList.remove('dragover');
            }, false);
        });

        // 處理文件放下
        oldDocDropArea.addEventListener('drop', function (e) {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                oldDocInput.files = files;
                uploadOldDocument();
            }
        }, false);
    }

    // AI 優化需求按鈕事件
    const optimizeBtn = document.getElementById('optimize-btn');
    if (optimizeBtn) {
        optimizeBtn.addEventListener('click', optimizeRequirements);
    }

    // 使用優化後的需求
    const useOptimizedBtn = document.getElementById('use-optimized-btn');
    if (useOptimizedBtn) {
        useOptimizedBtn.addEventListener('click', function () {
            const optimizedText = document.getElementById('optimized-requirements').value;
            document.getElementById('requirements').value = optimizedText;
            document.getElementById('optimized-section').style.display = 'none';
            alert('✅ 已使用優化後的需求');
        });
    }

    // 取消優化
    const cancelOptimizedBtn = document.getElementById('cancel-optimized-btn');
    if (cancelOptimizedBtn) {
        cancelOptimizedBtn.addEventListener('click', function () {
            document.getElementById('optimized-section').style.display = 'none';
            document.getElementById('optimized-requirements').value = '';
        });
    }

    // 恢復原始需求
    const revertOriginalBtn = document.getElementById('revert-original-btn');
    if (revertOriginalBtn) {
        revertOriginalBtn.addEventListener('click', function () {
            if (originalRequirements) {
                document.getElementById('requirements').value = originalRequirements;
                document.getElementById('optimized-requirements').value = originalRequirements;
                alert('✅ 已恢復原始需求');
            }
        });
    }
});
