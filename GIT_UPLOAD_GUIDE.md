# Git 上傳指南

## 快速開始腳本

### 步驟 1: 初始化並首次提交

```powershell
# 切換到專案目錄
cd c:\Users\TF000054\claude\doc_generator_v3

# 初始化 Git
git init

# 添加所有檔案
git add .

# 查看即將提交的檔案（建議執行）
git status

# 建立第一次提交
git commit -m "Initial commit: Document Generator v3

- Flask-based document generation system
- Support for Word, Excel, PowerPoint, PDF generation
- AI-powered SOP optimization
- Template management system
- Image preservation in documents"
```

---

### 步驟 2: 連結遠端儲存庫

**先在 GitHub/GitLab 建立新儲存庫，然後執行以下指令：**

#### GitHub 版本：
```powershell
git remote add origin https://github.com/您的使用者名稱/doc-generator-v3.git
git branch -M main
git push -u origin main
```

#### GitLab 版本：
```powershell
git remote add origin https://gitlab.com/您的使用者名稱/doc-generator-v3.git
git branch -M main
git push -u origin main
```

---

## 建立配置檔案範本（建議）

```powershell
# 建立 API 配置範本
New-Item -Path "config\api_config.json.example" -ItemType File -Force -Value '{"api_key": "YOUR_API_KEY_HERE", "api_base": "YOUR_API_BASE_URL"}'

# 提交範本檔案
git add config/api_config.json.example
git commit -m "Add API config template"
git push
```

---

## 日常使用指令

```powershell
# 查看狀態
git status

# 添加所有變更
git add .

# 提交變更（記得修改訊息）
git commit -m "描述您的變更"

# 推送到遠端
git push

# 拉取最新變更
git pull
```

---

## 使用 Git LFS 追蹤大檔案（選用）

如果 templates_storage 中有大型範本檔案：

```powershell
# 安裝 Git LFS
git lfs install

# 追蹤大型檔案
git lfs track "*.pptx"
git lfs track "*.docx"
git lfs track "*.xlsx"

# 提交 LFS 設定
git add .gitattributes
git commit -m "Add Git LFS tracking for Office files"
git push
```

---

## ⚠️ 重要提醒

### 已被 .gitignore 排除的檔案：
- ✅ `config/api_config.json` (API 金鑰)
- ✅ `venv/` (虛擬環境)
- ✅ `uploads/`, `output/`, `temp_images/` (使用者檔案)
- ✅ `*.log`, `api_cost_log.csv` (日誌)

### 絕對不要提交：
- ❌ API 金鑰或密碼
- ❌ 使用者上傳的檔案
- ❌ 虛擬環境
- ❌ 包含敏感資訊的配置檔

### 如果不小心提交了敏感資訊：
1. 立即更換 API 金鑰
2. 使用以下指令移除敏感檔案：
```powershell
# 從 Git 歷史中移除檔案（保留本地檔案）
git rm --cached config/api_config.json

# 提交變更
git commit -m "Remove sensitive config file"

# 強制推送
git push -f
```

---

## 設定 SSH 金鑰（建議）

避免每次推送都要輸入密碼：

```powershell
# 生成 SSH 金鑰
ssh-keygen -t ed25519 -C "your_email@example.com"

# 複製公鑰內容
Get-Content ~/.ssh/id_ed25519.pub | Set-Clipboard

# 然後到 GitHub/GitLab 設定中添加 SSH 金鑰
```

修改遠端 URL 為 SSH：
```powershell
git remote set-url origin git@github.com:您的使用者名稱/doc-generator-v3.git
```

---

## 分支管理

```powershell
# 建立新分支
git checkout -b feature/new-feature

# 切換分支
git checkout main

# 合併分支
git merge feature/new-feature

# 刪除分支
git branch -d feature/new-feature
```

---

## 疑難排解

### 推送被拒絕
```powershell
# 先拉取遠端變更
git pull --rebase origin main

# 再推送
git push
```

### 查看提交歷史
```powershell
git log --oneline --graph --all
```

### 撤銷最後一次提交（保留變更）
```powershell
git reset --soft HEAD~1
```

### 撤銷最後一次提交（丟棄變更）
```powershell
git reset --hard HEAD~1
```
