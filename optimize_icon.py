#!/usr/bin/env python3
"""
圖示優化工具
將 525KB 的圖示優化到 < 100KB
"""

import os
from pathlib import Path

def optimize_icon():
    """優化圖示檔案"""
    try:
        from PIL import Image

        # 讀取原始圖片
        input_path = 'static/icon.png'
        if not os.path.exists(input_path):
            print(f"❌ 找不到檔案: {input_path}")
            return False

        # 備份原始檔案
        backup_path = 'static/icon_original.png'
        if not os.path.exists(backup_path):
            os.rename(input_path, backup_path)
            print(f"✅ 已備份原始檔案到: {backup_path}")

        # 開啟圖片
        img = Image.open(backup_path)
        print(f"\n📊 原始圖片資訊:")
        print(f"   - 格式: {img.format}")
        print(f"   - 尺寸: {img.size}")
        print(f"   - 模式: {img.mode}")
        print(f"   - 大小: {os.path.getsize(backup_path) / 1024:.2f} KB")

        # 轉換為 RGB (如果是 RGBA 或其他模式)
        if img.mode == 'RGBA':
            # 建立白色背景
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])  # 使用 alpha 通道作為遮罩
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # 生成多種尺寸和格式的圖示
        sizes_and_formats = [
            # (尺寸, 檔名, 格式, 品質, 說明)
            (512, 'static/icon.png', 'PNG', 85, '主要圖示 (PNG)'),
            (256, 'static/icon-256.png', 'PNG', 85, '中等尺寸 (PNG)'),
            (128, 'static/icon-128.png', 'PNG', 85, '小尺寸 (PNG)'),
            (64, 'static/icon-64.png', 'PNG', 85, '縮圖 (PNG)'),
            (512, 'static/icon.jpg', 'JPEG', 85, '主要圖示 (JPEG)'),
            (256, 'static/icon-256.jpg', 'JPEG', 85, '中等尺寸 (JPEG)'),
            (32, 'static/favicon.ico', 'ICO', None, 'Favicon'),
        ]

        print(f"\n🔄 開始優化...")
        results = []

        for size, output_path, fmt, quality, desc in sizes_and_formats:
            try:
                # 調整尺寸
                resized = img.resize((size, size), Image.Resampling.LANCZOS)

                # 儲存
                if fmt == 'ICO':
                    resized.save(output_path, format=fmt)
                elif fmt == 'PNG':
                    resized.save(output_path, format=fmt, optimize=True, quality=quality)
                elif fmt == 'JPEG':
                    resized.save(output_path, format=fmt, optimize=True, quality=quality)

                # 檢查大小
                file_size = os.path.getsize(output_path) / 1024
                results.append({
                    'desc': desc,
                    'path': output_path,
                    'size': file_size,
                    'dimensions': f"{size}x{size}"
                })

            except Exception as e:
                print(f"   ⚠️  {desc} 生成失敗: {e}")

        # 顯示結果
        print(f"\n✅ 優化完成！\n")
        print(f"{'描述':<20} {'檔案':<25} {'尺寸':<12} {'大小':<10}")
        print("=" * 70)

        for r in results:
            size_indicator = "✅" if r['size'] < 100 else "⚠️"
            print(f"{r['desc']:<20} {r['path']:<25} {r['dimensions']:<12} {size_indicator} {r['size']:>6.2f} KB")

        # 計算節省空間
        original_size = os.path.getsize(backup_path) / 1024
        main_optimized_size = next((r['size'] for r in results if r['path'] == 'static/icon.png'), 0)
        saved = original_size - main_optimized_size
        saved_percent = (saved / original_size) * 100

        print("\n" + "=" * 70)
        print(f"📊 優化統計:")
        print(f"   原始檔案: {original_size:.2f} KB")
        print(f"   優化後:   {main_optimized_size:.2f} KB")
        print(f"   節省:     {saved:.2f} KB ({saved_percent:.1f}%)")

        return True

    except ImportError:
        print("❌ 錯誤：需要安裝 Pillow")
        print("\n請執行:")
        print("   pip install Pillow")
        return False

    except Exception as e:
        print(f"❌ 優化失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 70)
    print("🎨 圖示優化工具")
    print("=" * 70)

    success = optimize_icon()

    if success:
        print("\n✅ 所有圖示已成功優化！")
        print("\n📝 建議:")
        print("   1. 在 HTML 中使用 <img src='/static/icon.png'> (主要圖示)")
        print("   2. 根據需要使用不同尺寸的圖示")
        print("   3. 檢查 static/icon_original.png 是否為備份")
        print("   4. 測試圖示在網頁上的顯示效果")
    else:
        print("\n❌ 優化失敗，請檢查錯誤訊息")
