#!/bin/bash
###############################################################################
# 圖示快速優化腳本
# 使用 ImageMagick 優化圖示檔案
###############################################################################

echo "========================================================================"
echo "🎨 圖示快速優化工具"
echo "========================================================================"
echo ""

# 檢查 ImageMagick 是否已安裝
if ! command -v convert &> /dev/null; then
    echo "⚠️  ImageMagick 未安裝"
    echo ""
    echo "請選擇安裝方式："
    echo ""
    echo "方式 1: 在 WSL/Ubuntu 中安裝"
    echo "  sudo apt update && sudo apt install imagemagick -y"
    echo ""
    echo "方式 2: 使用線上工具（最簡單）"
    echo "  🔗 https://tinypng.com/"
    echo "  🔗 https://squoosh.app/"
    echo ""
    echo "方式 3: 查看完整指南"
    echo "  cat ICON_OPTIMIZATION_GUIDE.md"
    echo ""
    exit 1
fi

# 檢查原始檔案
if [ ! -f "static/icon.png" ]; then
    echo "❌ 找不到檔案: static/icon.png"
    exit 1
fi

# 顯示原始檔案資訊
echo "📊 原始檔案資訊:"
ls -lh static/icon.png
file static/icon.png
echo ""

# 備份原始檔案
if [ ! -f "static/icon_original.png" ]; then
    echo "💾 備份原始檔案..."
    cp static/icon.png static/icon_original.png
    echo "✅ 已備份到: static/icon_original.png"
    echo ""
fi

# 開始優化
echo "🔄 開始優化圖示..."
echo ""

# 主圖示 512x512
echo "📦 生成主圖示 (512x512)..."
convert static/icon_original.png \
    -resize 512x512 \
    -quality 85 \
    -strip \
    -define png:compression-level=9 \
    static/icon.png

# 中等尺寸 256x256
echo "📦 生成中等尺寸圖示 (256x256)..."
convert static/icon_original.png \
    -resize 256x256 \
    -quality 85 \
    -strip \
    -define png:compression-level=9 \
    static/icon-256.png

# 小尺寸 128x128
echo "📦 生成小尺寸圖示 (128x128)..."
convert static/icon_original.png \
    -resize 128x128 \
    -quality 85 \
    -strip \
    -define png:compression-level=9 \
    static/icon-128.png

# 縮圖 64x64
echo "📦 生成縮圖 (64x64)..."
convert static/icon_original.png \
    -resize 64x64 \
    -quality 85 \
    -strip \
    -define png:compression-level=9 \
    static/icon-64.png

# Favicon 32x32
echo "📦 生成 Favicon (32x32)..."
convert static/icon_original.png \
    -resize 32x32 \
    static/favicon.ico

echo ""
echo "✅ 優化完成！"
echo ""

# 顯示結果
echo "========================================================================"
echo "📊 優化結果"
echo "========================================================================"
echo ""
printf "%-30s %10s %12s\n" "檔案" "大小" "尺寸"
echo "------------------------------------------------------------------------"

# 原始檔案
original_size=$(stat -f%z static/icon_original.png 2>/dev/null || stat -c%s static/icon_original.png 2>/dev/null)
original_kb=$((original_size / 1024))
printf "%-30s %7d KB %12s\n" "icon_original.png (備份)" "$original_kb" "1024x1024"

# 優化後的檔案
for file in icon.png icon-256.png icon-128.png icon-64.png favicon.ico; do
    if [ -f "static/$file" ]; then
        size=$(stat -f%z "static/$file" 2>/dev/null || stat -c%s "static/$file" 2>/dev/null)
        kb=$((size / 1024))

        # 判斷尺寸
        case $file in
            icon.png) dim="512x512" ;;
            icon-256.png) dim="256x256" ;;
            icon-128.png) dim="128x128" ;;
            icon-64.png) dim="64x64" ;;
            favicon.ico) dim="32x32" ;;
        esac

        # 判斷是否符合目標
        if [ "$kb" -lt 100 ]; then
            status="✅"
        else
            status="⚠️"
        fi

        printf "%-30s %7d KB %12s %s\n" "$file" "$kb" "$dim" "$status"
    fi
done

echo ""
echo "========================================================================"

# 計算節省空間
optimized_size=$(stat -f%z static/icon.png 2>/dev/null || stat -c%s static/icon.png 2>/dev/null)
optimized_kb=$((optimized_size / 1024))
saved_kb=$((original_kb - optimized_kb))
saved_percent=$((saved_kb * 100 / original_kb))

echo "📈 優化統計:"
echo "   原始大小: $original_kb KB"
echo "   優化後:   $optimized_kb KB"
echo "   節省:     $saved_kb KB ($saved_percent%)"
echo ""

echo "✅ 所有圖示已成功生成！"
echo ""
echo "📝 後續步驟:"
echo "   1. 檢查圖示品質: open static/icon.png"
echo "   2. 更新 HTML 檔案使用新圖示"
echo "   3. 提交變更: git add static/icon*.png static/favicon.ico"
echo ""
echo "📚 詳細說明: cat ICON_OPTIMIZATION_GUIDE.md"
echo ""
