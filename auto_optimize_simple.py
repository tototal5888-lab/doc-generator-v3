#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動圖示優化工具 - 簡化版
"""

import os
import sys

def optimize():
    """優化圖示"""
    try:
        from PIL import Image

        print("=" * 70)
        print("圖示自動優化工具")
        print("=" * 70)
        print()

        # 檢查原始檔案
        input_path = 'static/icon.png'
        if not os.path.exists(input_path):
            print(f"錯誤: 找不到檔案 {input_path}")
            return False

        # 顯示原始資訊
        original_size = os.path.getsize(input_path)
        print(f"原始檔案:")
        print(f"  路徑: {input_path}")
        print(f"  大小: {original_size / 1024:.2f} KB")

        # 開啟圖片
        img = Image.open(input_path)
        print(f"  格式: {img.format}")
        print(f"  尺寸: {img.size}")
        print(f"  模式: {img.mode}")

        # 轉換為 RGB
        if img.mode == 'RGBA':
            print("\n轉換 RGBA 到 RGB...")
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode != 'RGB':
            print(f"\n轉換 {img.mode} 到 RGB...")
            img = img.convert('RGB')

        print(f"\n開始優化...")

        # 生成優化版本
        outputs = []

        # 512x512 主圖示
        print("  [1/5] 生成主圖示 (512x512)...")
        resized = img.resize((512, 512), Image.Resampling.LANCZOS)
        temp_path = 'static/icon_temp.png'
        resized.save(temp_path, 'PNG', optimize=True, quality=85)
        os.replace(temp_path, input_path)
        size_512 = os.path.getsize(input_path)
        outputs.append(('icon.png', 512, size_512))
        print(f"        完成: {size_512 / 1024:.2f} KB")

        # 256x256
        print("  [2/5] 生成中等尺寸 (256x256)...")
        resized_256 = img.resize((256, 256), Image.Resampling.LANCZOS)
        path_256 = 'static/icon-256.png'
        resized_256.save(path_256, 'PNG', optimize=True, quality=85)
        size_256 = os.path.getsize(path_256)
        outputs.append(('icon-256.png', 256, size_256))
        print(f"        完成: {size_256 / 1024:.2f} KB")

        # 128x128
        print("  [3/5] 生成小尺寸 (128x128)...")
        resized_128 = img.resize((128, 128), Image.Resampling.LANCZOS)
        path_128 = 'static/icon-128.png'
        resized_128.save(path_128, 'PNG', optimize=True, quality=85)
        size_128 = os.path.getsize(path_128)
        outputs.append(('icon-128.png', 128, size_128))
        print(f"        完成: {size_128 / 1024:.2f} KB")

        # 64x64
        print("  [4/5] 生成縮圖 (64x64)...")
        resized_64 = img.resize((64, 64), Image.Resampling.LANCZOS)
        path_64 = 'static/icon-64.png'
        resized_64.save(path_64, 'PNG', optimize=True, quality=85)
        size_64 = os.path.getsize(path_64)
        outputs.append(('icon-64.png', 64, size_64))
        print(f"        完成: {size_64 / 1024:.2f} KB")

        # Favicon 32x32
        print("  [5/5] 生成 Favicon (32x32)...")
        resized_32 = img.resize((32, 32), Image.Resampling.LANCZOS)
        path_32 = 'static/favicon.ico'
        resized_32.save(path_32, 'ICO')
        size_32 = os.path.getsize(path_32)
        outputs.append(('favicon.ico', 32, size_32))
        print(f"        完成: {size_32 / 1024:.2f} KB")

        # 顯示結果
        print("\n" + "=" * 70)
        print("優化結果")
        print("=" * 70)
        print()
        print(f"{'檔案':<25} {'尺寸':<12} {'大小':<12} {'狀態'}")
        print("-" * 70)

        for filename, size, filesize in outputs:
            size_kb = filesize / 1024
            status = "[OK]" if size_kb < 100 else "[WARN]"
            print(f"{filename:<25} {size}x{size:<8} {size_kb:>6.2f} KB    {status}")

        # 計算節省
        saved = original_size - size_512
        percent = (saved / original_size) * 100

        print()
        print("=" * 70)
        print("優化統計:")
        print(f"  原始大小: {original_size / 1024:.2f} KB")
        print(f"  優化後:   {size_512 / 1024:.2f} KB")
        print(f"  節省:     {saved / 1024:.2f} KB ({percent:.1f}%)")

        # 評級
        if size_512 < 100 * 1024 and percent > 60:
            if percent >= 80:
                grade = "A+"
            elif percent >= 70:
                grade = "A"
            else:
                grade = "B+"
            print(f"  等級:     {grade}")
            print()
            print(">>> 優化成功!")
        else:
            print()
            print(">>> 優化完成，但可能需要進一步處理")
            if size_512 >= 100 * 1024:
                print("    建議: 使用線上工具 (TinyPNG) 進一步壓縮")

        print("=" * 70)
        print()
        print("後續步驟:")
        print("  1. 執行 verify_optimization.sh 驗證結果")
        print("  2. 執行 python run.py 啟動應用測試")
        print("  3. 在瀏覽器中檢查圖示顯示效果")
        print()

        return True

    except ImportError:
        print("錯誤: Pillow 未安裝")
        print()
        print("請安裝 Pillow:")
        print("  venv\\Scripts\\pip.exe install Pillow")
        return False
    except Exception as e:
        print(f"錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = optimize()
    sys.exit(0 if success else 1)
