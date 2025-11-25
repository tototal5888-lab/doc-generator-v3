# 環境變數配置說明

## 配置方式

本專案支援兩種配置方式：

### 1. 環境變數配置（推薦）

使用 `.env` 文件配置，更安全且不會被提交到 Git。

**步驟：**

1. 複製 `.env.example` 為 `.env`：
   ```bash
   copy .env.example .env
   ```

2. 編輯 `.env` 文件，填入您的實際配置：
   ```bash
   # API 設定密碼
   ADMIN_PASSWORD=your_password_here
   
   # Flask 密鑰
   SECRET_KEY=your_secret_key_here
   
   # AI API 密鑰
   GEMINI_API_KEY=your_gemini_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   
   # AI 引擎設定
   API_TYPE=gemini
   OPENAI_MODEL=gpt-4o-mini
   ```

### 2. 網頁界面配置

在應用程式的「API設定」頁面中配置（需要管理員密碼）。

## 配置優先級

**環境變數 > 網頁配置**

- 如果 `.env` 文件中有配置，會優先使用環境變數
- 網頁配置會保存到 `config/api_config.json`
- 環境變數會覆蓋 JSON 文件中的相同配置

## 安全性

### ✅ 推薦做法
- 將敏感信息（API KEY、密碼）存放在 `.env` 文件中
- `.env` 文件已被 `.gitignore` 排除，不會被提交到 Git
- 使用強密碼作為 `ADMIN_PASSWORD`

### ❌ 不推薦做法
- 不要將 `.env` 文件提交到 Git
- 不要在代碼中硬編碼 API KEY
- 不要分享您的 `.env` 文件

## 配置項說明

| 配置項 | 說明 | 預設值 |
|--------|------|--------|
| `ADMIN_PASSWORD` | API 設定頁面的管理員密碼 | `sunon` |
| `SECRET_KEY` | Flask 應用程式密鑰 | `dev-key-12345` |
| `GEMINI_API_KEY` | Google Gemini API 密鑰 | 無 |
| `OPENAI_API_KEY` | OpenAI API 密鑰 | 無 |
| `API_TYPE` | 使用的 AI 引擎 (`gemini`/`openai`/`mock`) | `gemini` |
| `OPENAI_MODEL` | OpenAI 模型名稱 | `gpt-4o-mini` |

## 獲取 API 密鑰

### Google Gemini API
1. 訪問：https://makersuite.google.com/app/apikey
2. 登入 Google 帳號
3. 創建新的 API 密鑰
4. 複製密鑰到 `.env` 文件

### OpenAI API
1. 訪問：https://platform.openai.com/api-keys
2. 登入 OpenAI 帳號
3. 創建新的 API 密鑰
4. 複製密鑰到 `.env` 文件

## 故障排除

### 問題：API KEY 不生效
**解決方案：**
1. 確認 `.env` 文件在專案根目錄
2. 確認 `.env` 文件格式正確（無多餘空格）
3. 重新啟動應用程式

### 問題：無法解鎖 API 設定
**解決方案：**
1. 檢查 `.env` 中的 `ADMIN_PASSWORD` 是否正確
2. 確認應用程式已重新啟動以載入新配置
