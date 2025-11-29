/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "C:/Users/TF000054/claude/doc_generator_v3/templates/**/*.html",
        "C:/Users/TF000054/claude/doc_generator_v3/static/js/**/*.js"
    ],
    theme: {
        extend: {},
    },
    plugins: [require("daisyui")],
    daisyui: {
        themes: [
            {
                soft: {
                    "primary": "#7c9885",           // 柔和的綠色 - 主要操作
                    "primary-content": "#ffffff",   // 主色文字
                    "secondary": "#a8b5c8",         // 柔和的藍灰色 - 次要操作
                    "secondary-content": "#ffffff", // 次要色文字
                    "accent": "#c9a88a",            // 溫暖的米色 - 強調色
                    "accent-content": "#ffffff",    // 強調色文字
                    "neutral": "#5a5a5a",           // 中性灰
                    "neutral-content": "#ffffff",   // 中性色文字
                    "base-100": "#f8f7f5",          // 背景色 - 溫暖的米白色
                    "base-200": "#eeede9",          // 次要背景 - 淺米色
                    "base-300": "#d9d7d0",          // 邊框/分隔線 - 柔和灰
                    "base-content": "#4a4a4a",      // 主要文字 - 深灰而非純黑
                    "info": "#8ab4d5",              // 信息提示 - 柔和藍色
                    "info-content": "#ffffff",      // 信息文字
                    "success": "#88b89d",           // 成功提示 - 柔和綠色
                    "success-content": "#ffffff",   // 成功文字
                    "warning": "#d4b896",           // 警告提示 - 柔和橙色
                    "warning-content": "#4a4a4a",   // 警告文字
                    "error": "#c99090",             // 錯誤提示 - 柔和紅色
                    "error-content": "#ffffff",     // 錯誤文字
                },
            },
            "light", // 保留原始 light 主題作為備選
            "dark", "cupcake", "bumblebee", "emerald", "corporate", "synthwave", "retro", "cyberpunk", "valentine", "halloween", "garden", "forest", "aqua", "lofi", "pastel", "fantasy", "wireframe", "black", "luxury", "dracula", "cmyk", "autumn", "business", "acid", "lemonade", "night", "coffee", "winter"
        ],
    },
}
