---
description: AI-powered design intelligence with 50+ styles, 95+ color palettes, and automated design system generation
---

# UI UX Pro Max Skill

這個 skill 提供智慧型 UI/UX 設計建議，包含：
- **67 種 UI 風格** - Glassmorphism、Claymorphism、Minimalism、Brutalism、Neumorphism、Bento Grid、Dark Mode、AI-Native UI 等
- **96 種色彩調色盤** - 針對 SaaS、電商、醫療、金融、美容等產業
- **56 種字型配對** - 精選的字體組合，包含 Google Fonts 匯入
- **100 條推理規則** - 依產業自動生成完整設計系統

## 使用方式

直接使用斜線命令：

```
/ui-ux-pro-max 為我的 SaaS 產品建立一個 landing page
```

或透過自然語言請求：

```
建立一個醫療分析儀表板
設計一個具有深色模式的作品集網站
製作一個電商行動應用程式 UI
建立一個金融銀行應用程式，使用深色主題
```

## 運作原理

1. **您提出請求** - 要求任何 UI/UX 任務（建立、設計、製作、實作、審查、修復、改進）
2. **設計系統生成** - AI 自動使用推理引擎生成完整的設計系統
3. **智慧推薦** - 根據您的產品類型和需求，找出最佳匹配的風格、顏色和字體
4. **程式碼生成** - 使用適當的顏色、字體、間距和最佳實踐來實作 UI
5. **交付前檢查** - 針對常見的 UI/UX 反模式進行驗證

## 進階使用：設計系統命令

直接存取設計系統生成器：

```bash
# 以 ASCII 輸出生成設計系統
python3 .agent/skills/ui-ux-pro-max/scripts/search.py "beauty spa wellness" --design-system -p "Serenity Spa"

# 以 Markdown 輸出生成
python3 .agent/skills/ui-ux-pro-max/scripts/search.py "fintech banking" --design-system -f markdown

# 特定領域搜尋
python3 .agent/skills/ui-ux-pro-max/scripts/search.py "glassmorphism" --domain style
python3 .agent/skills/ui-ux-pro-max/scripts/search.py "elegant serif" --domain typography

# 儲存設計系統到檔案
python3 .agent/skills/ui-ux-pro-max/scripts/search.py "SaaS dashboard" --design-system --persist -p "MyApp"
```

## 支援的技術堆疊

- **Web (HTML)**: HTML + Tailwind（預設）
- **React 生態系**: React、Next.js、shadcn/ui
- **Vue 生態系**: Vue、Nuxt.js、Nuxt UI
- **其他 Web**: Svelte、Astro
- **iOS**: SwiftUI
- **Android**: Jetpack Compose
- **跨平台**: React Native、Flutter
