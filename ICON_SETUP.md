# 專案圖示設定說明

## 圖示位置
- **檔案路徑**: `static/icon.png`
- **圖示風格**: 3D 等距風格，簡化版
- **主題**: 書本 + 筆

## HTML 引用
圖示已在 `templates/index_v3.html` 的 `<head>` 區塊中正確引用：

```html
<!-- Favicon and App Icons -->
<link rel="icon" type="image/png" href="/static/icon.png">
<link rel="apple-touch-icon" href="/static/icon.png">
<link rel="shortcut icon" type="image/png" href="/static/icon.png">
```

## 支援平台
- ✅ 瀏覽器標籤頁 (Favicon)
- ✅ 書籤/收藏夾
- ✅ iOS 主畫面 (Apple Touch Icon)
- ✅ Android 主畫面
- ✅ Windows 工作列

## 效果
重新啟動應用程式後，在瀏覽器中訪問 http://localhost:5000，您將看到：
1. 瀏覽器標籤頁顯示新圖示
2. 將網站添加到書籤時顯示圖示
3. 在行動裝置上添加到主畫面時顯示圖示

## Git 提交
圖示檔案會被正確提交到 Git 倉庫（未被 .gitignore 排除）。
