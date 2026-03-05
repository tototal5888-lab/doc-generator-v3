// ==================== 人員確認相關功能 ====================

/**
 * 上傳 Excel 後自動選取全部人員，等待 User 手動點擊生成
 * @param {Array} users - 人員列表
 * @param {boolean} hasMultiple - 是否為多人員
 */
function showUsersConfirmation(users, hasMultiple) {
    console.log('[INFO] 識別到人員，自動選取全部:', users);

    // 自動選取所有人員，不跳出確認 UI，等待 User 手動操作
    window.selectedUsers = users.map(u => u.name);
    console.log('[INFO] 已自動選擇人員:', window.selectedUsers);
    console.log('[INFO] Excel 檔案:', window.excelTempFilename);
}
