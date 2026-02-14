// ==================== 人員確認相關功能 ====================

/**
 * 顯示人員確認界面
 * @param {Array} users - 人員列表
 * @param {boolean} hasMultiple - 是否為多人員
 */
function showUsersConfirmation(users, hasMultiple) {
    const section = document.getElementById('users-confirmation-section');
    const usersList = document.getElementById('users-list');

    if (!section || !usersList) {
        console.error('[ERROR] 找不到人員確認界面元素');
        return;
    }

    console.log('[INFO] 顯示人員確認界面:', users);

    // 生成人員列表
    usersList.innerHTML = users.map((user, index) => `
        <label class="flex items-center gap-3 p-3 bg-base-200 rounded-lg cursor-pointer hover:bg-base-300 transition-colors">
            <input type="checkbox" 
                   class="checkbox checkbox-primary" 
                   data-user="${user.name}"
                   ${user.selected ? 'checked' : ''}
            />
            <div class="flex-1">
                <div class="font-semibold text-base">${user.name}</div>
                <div class="text-sm opacity-60">${user.data_count.toLocaleString()} 字元資料</div>
            </div>
        </label>
    `).join('');

    // 顯示區塊並滾動到視窗
    section.style.display = 'block';
    setTimeout(() => {
        section.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

// 頁面載入時初始化人員確認按鈕
document.addEventListener('DOMContentLoaded', function () {
    // 確認並生成報告按鈕
    const confirmUsersBtn = document.getElementById('confirm-users-btn');
    if (confirmUsersBtn) {
        confirmUsersBtn.addEventListener('click', function () {
            // 收集選中的人員
            const checkboxes = document.querySelectorAll('#users-list input[type=checkbox]:checked');
            const selectedUsers = Array.from(checkboxes).map(cb => cb.dataset.user);

            if (selectedUsers.length === 0) {
                alert('⚠️ 請至少選擇一位人員');
                return;
            }

            // 儲存選定的人員,供 generateDocument 使用
            window.selectedUsers = selectedUsers;
            // window.excelTempFilename 已在 uploadOldDocument 時設置,這裡不需要重複設置

            console.log('[INFO] 已選擇人員:', selectedUsers);
            console.log('[INFO] Excel 檔案:', window.excelTempFilename);

            // 隱藏確認界面
            document.getElementById('users-confirmation-section').style.display = 'none';

            // 提示用戶可以生成了並自動觸發生成
            const generateBtn = document.getElementById('generate-btn');
            if (generateBtn) {
                // 直接觸發生成
                generateDocument();
            } else {
                alert(`✅ 已選擇 ${selectedUsers.length} 位人員,請點擊「生成文檔」按鈕`);
            }
        });
    }

    // 取消按鈕
    const cancelUsersBtn = document.getElementById('cancel-users-btn');
    if (cancelUsersBtn) {
        cancelUsersBtn.addEventListener('click', function () {
            // 清除選擇
            window.selectedUsers = null;
            window.excelTempFilename = null;
            window.excelUsers = null;

            // 隱藏確認界面
            document.getElementById('users-confirmation-section').style.display = 'none';

            // 重置上傳區域
            const dropArea = document.getElementById('old-doc-drop-area');
            if (dropArea) {
                dropArea.innerHTML = `
                    <div class="text-center py-8">
                        <span class="text-6xl">📄</span>
                        <div class="mt-4 text-lg font-medium">拖曳檔案到此處 或點擊選擇</div>
                        <div class="text-sm opacity-60 mt-2">支援 PPTX, DOCX, PDF, TXT, XLSX, XLS</div>
                    </div>
                `;
            }
        });
    }
});
