#!/bin/bash
###############################################################################
# 圖示優化驗證腳本
# 檢查優化是否成功完成
###############################################################################

echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║              🔍 圖示優化驗證工具                                         ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

# 檢查檔案是否存在
check_file_exists() {
    local file=$1
    if [ -f "$file" ]; then
        echo "✅"
        return 0
    else
        echo "❌"
        return 1
    fi
}

# 檢查檔案大小
get_file_size_kb() {
    local file=$1
    if [ -f "$file" ]; then
        stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null
    else
        echo "0"
    fi
}

# 顯示分隔線
separator() {
    echo "────────────────────────────────────────────────────────────────────────"
}

# 主要檢查
echo "📋 檔案狀態檢查"
separator

# 1. 檢查原始備份
echo -n "1. 原始檔案備份 (icon_original.png)     "
exists=$(check_file_exists "static/icon_original.png")
echo "$exists"

# 2. 檢查優化檔案
echo -n "2. 優化後檔案 (icon.png)                 "
exists=$(check_file_exists "static/icon.png")
echo "$exists"

echo ""

# 詳細資訊
if [ -f "static/icon_original.png" ] && [ -f "static/icon.png" ]; then
    echo "📊 檔案大小對比"
    separator

    original_bytes=$(get_file_size_kb "static/icon_original.png")
    optimized_bytes=$(get_file_size_kb "static/icon.png")

    original_kb=$((original_bytes / 1024))
    optimized_kb=$((optimized_bytes / 1024))

    echo "原始檔案大小：  ${original_kb} KB"
    echo "優化後大小：    ${optimized_kb} KB"

    if [ $optimized_bytes -lt $original_bytes ]; then
        saved=$((original_bytes - optimized_bytes))
        saved_kb=$((saved / 1024))
        percent=$((saved * 100 / original_bytes))
        echo "節省空間：      ${saved_kb} KB (${percent}%)"
    else
        echo "⚠️  警告：優化後檔案沒有變小"
    fi

    echo ""
    echo "📏 目標達成檢查"
    separator

    # 檢查是否達到目標
    if [ $optimized_kb -lt 100 ]; then
        echo "✅ 主圖示 < 100 KB              [PASS] ${optimized_kb} KB"
    else
        echo "❌ 主圖示 < 100 KB              [FAIL] ${optimized_kb} KB"
    fi

    if [ $percent -gt 50 ]; then
        echo "✅ 節省空間 > 50%               [PASS] ${percent}%"
    else
        echo "⚠️  節省空間 > 50%               [WARN] ${percent}%"
    fi

    # 檢查檔案修改時間
    original_time=$(stat -c%Y "static/icon_original.png" 2>/dev/null || stat -f%m "static/icon_original.png" 2>/dev/null)
    optimized_time=$(stat -c%Y "static/icon.png" 2>/dev/null || stat -f%m "static/icon.png" 2>/dev/null)

    if [ $optimized_time -gt $original_time ]; then
        echo "✅ 檔案已更新                   [PASS]"
    else
        echo "⚠️  檔案已更新                   [WARN] 檔案可能未替換"
    fi

    echo ""
    echo "🎯 優化等級評估"
    separator

    if [ $percent -ge 80 ]; then
        grade="A+ (優秀)"
        emoji="🏆"
    elif [ $percent -ge 70 ]; then
        grade="A (良好)"
        emoji="🎉"
    elif [ $percent -ge 60 ]; then
        grade="B (不錯)"
        emoji="👍"
    elif [ $percent -ge 50 ]; then
        grade="C (及格)"
        emoji="✅"
    else
        grade="D (需改進)"
        emoji="⚠️"
    fi

    echo "$emoji 優化等級：$grade"
    echo "   壓縮比例：${percent}%"
    echo "   檔案大小：${optimized_kb} KB"

    echo ""
    echo "════════════════════════════════════════════════════════════════════════"

    # 最終結論
    if [ $optimized_kb -lt 100 ] && [ $percent -gt 50 ]; then
        echo "🎉 優化成功！圖示已達到效能目標"
        echo ""
        echo "建議後續步驟："
        echo "  1. 在瀏覽器中測試顯示效果"
        echo "  2. 檢查 Network 面板的載入時間"
        echo "  3. 考慮生成多種尺寸 (執行 ./quick_optimize.sh)"
        echo "  4. 提交 Git 變更"
    else
        echo "⚠️  優化未完全達標"
        echo ""
        echo "建議："
        if [ $optimized_kb -ge 100 ]; then
            echo "  - 檔案仍然偏大，可以："
            echo "    1. 重新上傳到 TinyPNG 再壓縮一次"
            echo "    2. 使用 Squoosh 調整品質參數"
            echo "    3. 考慮降低解析度 (1024 → 512)"
        fi
        if [ $percent -le 50 ]; then
            echo "  - 壓縮比例不足，可能："
            echo "    1. 檔案沒有真正被替換"
            echo "    2. TinyPNG 優化效果有限"
            echo "    3. 嘗試其他工具 (Squoosh, ImageMagick)"
        fi
    fi

else
    echo "❌ 錯誤：找不到必要的檔案"
    echo ""
    echo "請確認："
    echo "  1. static/icon_original.png 是否存在（備份檔案）"
    echo "  2. static/icon.png 是否存在（優化後檔案）"
    echo ""
    echo "如需重新開始，請執行："
    echo "  cat TINYPNG_STEP_BY_STEP.md"
fi

echo "════════════════════════════════════════════════════════════════════════"
echo ""

# 顯示檔案列表
echo "📁 當前檔案列表"
separator
ls -lh static/icon*.png 2>/dev/null || echo "找不到圖示檔案"
echo ""

# 顯示檔案類型
echo "🔍 檔案類型資訊"
separator
for file in static/icon*.png; do
    if [ -f "$file" ]; then
        echo "$(basename $file):"
        file "$file" | sed 's/^/  /'
    fi
done

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo ""
echo "💡 提示："
echo "   - 執行 'python run.py' 啟動應用測試"
echo "   - 執行 'cat TINYPNG_STEP_BY_STEP.md' 查看完整步驟"
echo "   - 執行 './quick_optimize.sh' 生成多種尺寸"
echo ""
