// ==================== 文檔生成相關 ====================

// 儲存原始需求
let originalRequirements = '';
// 追蹤是否已執行 AI 優化
let hasOptimized = false;

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

    // 檢查是否已執行 AI 優化
    // Excel 多人員流程不需要此提示
    const isExcelFlow = window.excelUsers && window.excelUsers.length > 0;
    if (!hasOptimized && !isExcelFlow && requirements.trim()) {
        const confirmed = confirm(
            '⚠️ 提醒：您尚未執行 AI 優化需求\n\n' +
            '建議先點擊「✨ AI 優化需求」按鈕，可以幫助您：\n' +
            '• 整理並結構化需求內容\n' +
            '• 去除重複資料\n' +
            '• 提升文檔品質\n\n' +
            '是否要繼續生成文檔？\n\n' +
            '點擊「取消」返回優化需求\n' +
            '點擊「確定」直接生成文檔'
        );

        if (!confirmed) {
            return; // 用戶選擇取消，不執行生成
        }
    }

    // generateBtn.innerHTML = '<span class="spinner"></span> 生成中...';
    // generateBtn.disabled = true;

    // 顯示恐龍跑跑動畫模態框
    const loadingModal = document.getElementById('loading-modal');
    if (loadingModal) {
        loadingModal.showModal();
    } else {
        // Fallback if modal not found
        generateBtn.innerHTML = '<span class="spinner"></span> 生成中...';
        generateBtn.disabled = true;
    }

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

        // 調試日誌：顯示當前 window 變數狀態
        console.log('[DEBUG] generateDocument 開始執行');
        console.log('[DEBUG] window.selectedUsers:', window.selectedUsers);
        console.log('[DEBUG] window.excelTempFilename:', window.excelTempFilename);
        console.log('[DEBUG] window.excelUsers:', window.excelUsers);

        // 備援邏輯：如果 selectedUsers 未設定（使用者跳過確認按鈕直接生成），
        // 但仍有 excelUsers，則自動使用全部人員
        if (!window.selectedUsers && window.excelUsers && window.excelUsers.length > 0) {
            window.selectedUsers = window.excelUsers.map(u => u.name || u);
            console.log('[INFO] 備援：自動使用全部 Excel 人員:', window.selectedUsers);
        }

        // 如果有選定的人員列表，添加到請求中
        if (window.selectedUsers && window.excelTempFilename) {
            requestData.selected_users = window.selectedUsers;
            requestData.excel_temp_filename = window.excelTempFilename;
            console.log('[INFO] ✅ 傳送選定人員:', window.selectedUsers);
            console.log('[INFO] ✅ Excel 檔名:', window.excelTempFilename);
        } else {
            console.log('[WARNING] ❌ 沒有選定人員資訊');
            console.log('[WARNING] selectedUsers 存在?', !!window.selectedUsers);
            console.log('[WARNING] excelTempFilename 存在?', !!window.excelTempFilename);
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
        // 關閉模態框
        if (loadingModal) {
            loadingModal.close();
        }

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

    // 檢查是否為多檔案結果 (只要 multiple 標記為真，即使只有一個檔案也用列表顯示)
    if (result.multiple && result.files) {
        // 多檔案模式
        let filesHTML = '';
        result.files.forEach((file, index) => {
            filesHTML += `
                <div class="flex items-center justify-between p-3 bg-base-200 rounded-lg mb-2">
                    <div class="flex-1">
                        <div class="font-semibold">${formatIcons[file.format] || '📄'} ${file.user}</div>
                        <div class="text-sm opacity-60">${file.filename}</div>
                    </div>
                    <a href="${API_BASE_URL}/download/${file.filename}" class="btn btn-sm btn-success">
                        ⬇️ 下載
                    </a>
                </div>
            `;
        });

        let failedHTML = '';
        if (result.failed && result.failed.length > 0) {
            failedHTML = `
                <div class="alert alert-warning mt-4">
                    <span>⚠️ 以下人員的報告生成失敗：</span>
                    <ul class="text-sm mt-2">
                        ${result.failed.map(f => `<li>${f.user}: ${f.error}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        resultContent.innerHTML = `
            <div class="alert alert-success show">
                <div>
                    <h3 class="font-bold text-lg mb-2">✅ 生成完成</h3>
                    <div style="font-size: 1.1rem; margin-bottom: 10px;">
                        已為 ${result.count} 位人員生成報告：
                    </div>
                    <div class="max-h-96 overflow-y-auto mb-4 custom-scrollbar">
                        ${filesHTML}
                    </div>
                    ${failedHTML}
                </div>
            </div>
        `;
    } else {
        // 單檔案模式（原有邏輯）
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
    dropArea.innerHTML = '<div class="text-center"><span class="loading loading-spinner loading-lg"></span><div class="mt-2">提取中...</div></div>';

    try {
        const response = await fetch(`${API_BASE_URL}/extract_text`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            document.getElementById('requirements').value = data.content;

            // 檢查是否有人員資訊（Excel 工作報告）
            if (data.users && data.users.length > 0) {
                // 儲存 Excel 資訊供後續使用
                window.excelTempFilename = data.excel_temp_filename;
                window.excelUsers = data.users;

                // 顯示人員確認界面
                showUsersConfirmation(data.users, data.has_multiple_users);

                // 更新上傳區域顯示
                dropArea.innerHTML = `
                    <div class="text-center">
                        <span class="text-5xl">📋</span>
                        <div class="mt-2 font-medium text-success">已上傳: ${file.name}</div>
                        <div class="text-sm opacity-60 mt-1">已識別 ${data.users.length} 位人員</div>
                        <div class="text-xs opacity-40 mt-1">請向下查看人員列表並確認</div>
                    </div>
                `;
                return;
            }

            // 顯示已上傳的檔案名稱和訊息（不彈窗）
            let message = '內容提取成功';
            if (data.images) {
                window.extractedImageFolder = data.images.folder;
                message = `內容提取成功，共 ${data.images.count} 張圖片`;
            } else {
                window.extractedImageFolder = null;
            }

            dropArea.innerHTML = `
                <div class="text-center">
                    <span class="text-5xl">✅</span>
                    <div class="mt-2 font-medium text-success">已上傳: ${file.name}</div>
                    <div class="text-sm opacity-60 mt-1">${message}</div>
                    <div class="text-xs opacity-40 mt-1">點擊可重新選擇檔案</div>
                </div>
            `;
        } else {
            // 顯示錯誤訊息（不彈窗）
            dropArea.innerHTML = `
                <div class="text-center">
                    <span class="text-5xl">❌</span>
                    <div class="mt-2 font-medium text-error">${data.error || '提取失敗'}</div>
                    <div class="text-sm opacity-60 mt-1">點擊重新選擇檔案</div>
                </div>
            `;
        }
    } catch (error) {
        // 顯示錯誤訊息（不彈窗）
        dropArea.innerHTML = `
            <div class="text-center">
                <span class="text-5xl">❌</span>
                <div class="mt-2 font-medium text-error">提取失敗: ${error.message}</div>
                <div class="text-sm opacity-60 mt-1">點擊重新選擇檔案</div>
            </div>
        `;
        // 錯誤時恢復原始狀態
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
    const generateBtn = document.getElementById('generate-btn');

    btn.disabled = true;
    btnText.style.display = 'none';
    btnLoading.style.display = 'inline';

    // 顯示恐龍/馬力歐跑跑動畫模態框
    const loadingModal = document.getElementById('loading-modal');
    if (loadingModal) {
        loadingModal.showModal();
        /* Update loading text if possible */
        const title = loadingModal.querySelector('h3');
        if (title) title.textContent = '🧠 AI 正在優化需求中...';
    }

    // 禁用生成文檔按鈕
    if (generateBtn) {
        generateBtn.disabled = true;
    }

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
            // 標記已執行優化
            hasOptimized = true;

            // 顯示優化結果區域
            document.getElementById('optimized-section').style.display = 'block';
            document.getElementById('optimized-requirements').value = data.optimized_requirements;

            // 平滑滾動到優化結果
            document.getElementById('optimized-section').scrollIntoView({
                behavior: 'smooth',
                block: 'nearest'
            });

            // 成功提示
            const alertElement = document.getElementById('generate-alert');
            if (alertElement) {
                showAlert(alertElement, 'success', '✨ 需求優化完成！');
            }
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

        // 關閉模態框
        if (loadingModal) {
            loadingModal.close();
            // Reset title for next use if needed
            const title = loadingModal.querySelector('h3');
            if (title) title.textContent = '🎰 文檔生成中...';
        }

        // 恢復生成文檔按鈕
        if (generateBtn) {
            generateBtn.disabled = false;
        }
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
            const oldDocUploadLabel = document.getElementById('old-doc-upload-label');

            if (this.value === 'sop_optimize') {
                requirementsLabel.textContent = '舊 SOP 內容';
                requirementsTextarea.placeholder = '請在此貼上您想要優化的舊 SOP 文檔內容...\\n\\n或使用上方的「上傳舊文檔」功能自動提取內容';
                oldDocUploadSection.style.display = 'block';
                if (oldDocUploadLabel) oldDocUploadLabel.textContent = '上傳舊文檔（可選）';
            } else if (this.value === 'work_report') {
                requirementsLabel.textContent = '工作報告資料';
                requirementsTextarea.placeholder = '請在此貼上您的工作報告資料（會議、工作項目等）...\\n\\n或使用上方的「上傳工作報告」功能自動提取 Excel 內容';
                oldDocUploadSection.style.display = 'block';
                if (oldDocUploadLabel) oldDocUploadLabel.textContent = '上傳工作報告 Excel（可選）';
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
            // 使用優化後的需求時，保持 hasOptimized 標記為 true
            hasOptimized = true;
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

    // 監聽需求內容變更，重置優化標記
    const requirementsInput = document.getElementById('requirements');
    if (requirementsInput) {
        let lastValue = requirementsInput.value;
        requirementsInput.addEventListener('input', function () {
            // 只有當內容真的改變時才重置標記
            if (this.value !== lastValue) {
                hasOptimized = false;
                lastValue = this.value;
            }
        });
    }
});
