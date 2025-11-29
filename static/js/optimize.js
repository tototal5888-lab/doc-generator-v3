// ==================== 優化簡報相關 ====================

// 儲存已上傳的圖片信息
let stagedImages = [];

/**
 * 載入已生成的 PPTX 文件列表
 */
async function loadPPTXFiles() {
    console.log('loadPPTXFiles() called');
    try {
        const response = await fetch(`${API_BASE_URL}/history`);
        const documents = await response.json();

        console.log('Fetched documents:', documents);

        const select = document.getElementById('source-pptx-select');
        if (!select) {
            console.error('source-pptx-select element not found!');
            return;
        }

        select.innerHTML = '<option value="">請選擇已生成的 PPTX 文件...</option>';

        // 只顯示 PPTX 文件
        const pptxFiles = documents.filter(doc => doc.filename.endsWith('.pptx'));

        console.log('PPTX files found:', pptxFiles.length);

        pptxFiles.forEach(doc => {
            const option = document.createElement('option');
            option.value = doc.filename;
            option.textContent = `${doc.filename} (${doc.date})`;
            select.appendChild(option);
        });

    } catch (error) {
        console.error('載入 PPTX 文件列表失敗:', error);
    }
}

/**
 * 處理圖片上傳
 */
async function handleImageUpload(event) {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    const alertElement = document.getElementById('optimize-alert');

    for (let file of files) {
        try {
            const formData = new FormData();
            formData.append('image', file);

            const response = await fetch(`${API_BASE_URL}/stage_image`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                stagedImages.push({
                    filename: data.filename,
                    path: data.path,
                    originalName: file.name,
                    slideNumber: 1  // 預設頁碼
                });
            } else {
                showAlert(alertElement, 'error', `上傳 ${file.name} 失敗: ${data.error}`);
            }
        } catch (error) {
            showAlert(alertElement, 'error', `上傳 ${file.name} 失敗: ${error.message}`);
        }
    }

    // 更新圖片列表顯示
    updateImageList();

    // 清空 input
    event.target.value = '';
}

/**
 * 更新圖片列表顯示
 */
function updateImageList() {
    const listContainer = document.getElementById('optimize-image-list');
    const injectBtn = document.getElementById('inject-btn');

    if (stagedImages.length === 0) {
        listContainer.innerHTML = '<div class="text-sm opacity-60 text-center py-8">尚未上傳圖片</div>';
        injectBtn.disabled = true;
        return;
    }

    listContainer.innerHTML = '';

    stagedImages.forEach((img, index) => {
        const card = document.createElement('div');
        card.className = 'card bg-base-200 shadow-sm mb-2';
        card.innerHTML = `
            <div class="card-body p-4">
                <div class="flex items-center gap-4">
                    <div class="flex-1">
                        <div class="font-medium">${img.originalName}</div>
                        <div class="text-xs opacity-60">${img.filename}</div>
                    </div>
                    <div class="form-control">
                        <label class="label">
                            <span class="label-text text-xs">插入頁碼</span>
                        </label>
                        <input type="number" 
                               class="input input-bordered input-sm w-20" 
                               value="${img.slideNumber}" 
                               min="1"
                               onchange="updateImageSlideNumber(${index}, this.value)">
                    </div>
                    <button class="btn btn-error btn-sm" onclick="removeImage(${index})">
                        🗑️
                    </button>
                </div>
            </div>
        `;
        listContainer.appendChild(card);
    });

    // 啟用注入按鈕
    injectBtn.disabled = false;
}

/**
 * 更新圖片的目標頁碼
 */
function updateImageSlideNumber(index, slideNumber) {
    stagedImages[index].slideNumber = parseInt(slideNumber);
}

/**
 * 移除圖片
 */
function removeImage(index) {
    stagedImages.splice(index, 1);
    updateImageList();
}

/**
 * 執行圖片注入
 */
async function injectImages() {
    const sourceFilename = document.getElementById('source-pptx-select').value;
    const alertElement = document.getElementById('optimize-alert');
    const injectBtn = document.getElementById('inject-btn');

    if (!sourceFilename) {
        showAlert(alertElement, 'error', '❌ 請選擇源文件');
        return;
    }

    if (stagedImages.length === 0) {
        showAlert(alertElement, 'error', '❌ 請至少上傳一張圖片');
        return;
    }

    // 準備注入配置
    const injections = stagedImages.map(img => ({
        image_path: img.path,
        slide_number: img.slideNumber
    }));

    injectBtn.innerHTML = '<span class="spinner"></span> 處理中...';
    injectBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/inject_images`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: sourceFilename,
                injections: injections
            })
        });

        const data = await response.json();

        if (data.success) {
            showAlert(alertElement, 'success', `✅ 成功生成新版本: ${data.filename}`);

            // 顯示下載鏈接
            const downloadLink = document.createElement('a');
            downloadLink.href = data.download_url;
            downloadLink.className = 'btn btn-success mt-2';
            downloadLink.textContent = '⬇️ 下載新文件';
            alertElement.appendChild(downloadLink);

            // 清空表單
            clearOptimizeForm();

            // 重新載入文件列表
            loadPPTXFiles();
        } else {
            showAlert(alertElement, 'error', '❌ ' + (data.error || '注入失敗'));
        }
    } catch (error) {
        showAlert(alertElement, 'error', '❌ 注入失敗: ' + error.message);
    } finally {
        injectBtn.innerHTML = '✨ 生成新版本';
        injectBtn.disabled = false;
    }
}

/**
 * 清空優化表單
 */
function clearOptimizeForm() {
    document.getElementById('source-pptx-select').value = '';
    document.getElementById('optimize-image-input').value = '';
    stagedImages = [];
    updateImageList();

    const alertElement = document.getElementById('optimize-alert');
    alertElement.classList.add('hidden');
}

// ==================== 頁面初始化 ====================

// 當切換到優化簡報 Tab 時載入文件列表
document.addEventListener('DOMContentLoaded', () => {
    // 監聽圖片上傳
    const imageInput = document.getElementById('optimize-image-input');
    if (imageInput) {
        imageInput.addEventListener('change', handleImageUpload);
    }
});
