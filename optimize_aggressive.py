#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
激進壓縮 - 目標 < 100 KB
"""

import os
import sys

def optimize():
    try:
        from PIL import Image

        print("=" * 70)
        print("激進壓縮模式 - 目標 < 100 KB")
        print("=" * 70)
        print()

        input_path = 'static/icon.png'
        original_size = os.path.getsize(input_path)
        print(f"當前大小: {original_size / 1024:.2f} KB")
        print()

        # 開啟圖片
        img = Image.open(input_path)

        # 確保是 RGB
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # 嘗試不同的壓縮策略
        print("嘗試壓縮策略...")
        print()

        best_size = original_size
        best_quality = 85
        best_method = "原始"

        # 策略 1: 降低品質
        for quality in [80, 75, 70, 65, 60]:
            temp_path = 'static/icon_test.jpg'
            img.save(temp_path, 'JPEG', optimize=True, quality=quality)
            size = os.path.getsize(temp_path)
            print(f"  JPEG 品質 {quality}: {size / 1024:.2f} KB")
            if size < best_size:
                best_size = size
                best_quality = quality
                best_method = f"JPEG-{quality}"
            os.remove(temp_path)

        # 策略 2: 降低解析度再壓縮
        for new_size in [480, 420, 384, 360]:
            resized = img.resize((new_size, new_size), Image.Resampling.LANCZOS)
            temp_path = 'static/icon_test.jpg'
            resized.save(temp_path, 'JPEG', optimize=True, quality=80)
            size = os.path.getsize(temp_path)
            print(f"  解析度 {new_size}x{new_size}: {size / 1024:.2f} KB")
            if size < best_size and size < 100 * 1024:
                best_size = size
                best_method = f"{new_size}x{new_size}@80"
            os.remove(temp_path)

        print()
        print(f"最佳方案: {best_method}")
        print(f"預期大小: {best_size / 1024:.2f} KB")
        print()

        # 應用最佳方案
        if best_size < 100 * 1024:
            print("應用最佳壓縮方案...")

            if "JPEG-" in best_method:
                # 使用JPEG壓縮
                quality = int(best_method.split('-')[1])
                img.save(input_path, 'JPEG', optimize=True, quality=quality)
                print(f"已儲存為 JPEG，品質 {quality}")
            elif "x" in best_method:
                # 降低解析度
                size_val = int(best_method.split('x')[0])
                resized = img.resize((size_val, size_val), Image.Resampling.LANCZOS)
                resized.save(input_path, 'JPEG', optimize=True, quality=80)
                print(f"已調整為 {size_val}x{size_val}")

            final_size = os.path.getsize(input_path)
            print()
            print("=" * 70)
            print("壓縮完成!")
            print(f"  原始: {original_size / 1024:.2f} KB")
            print(f"  最終: {final_size / 1024:.2f} KB")
            print(f"  節省: {(original_size - final_size) / 1024:.2f} KB")
            print(f"  比例: {((original_size - final_size) * 100 / original_size):.1f}%")
            print("=" * 70)
            print()

            if final_size < 100 * 1024:
                print(">>> 成功! 檔案 < 100 KB")
            else:
                print(">>> 接近目標，建議使用 TinyPNG 最終優化")

            return True
        else:
            print("警告: 無法在不嚴重損失品質的情況下達到 < 100 KB")
            print()
            print("建議:")
            print("  1. 使用 TinyPNG: https://tinypng.com/")
            print("  2. 接受目前的 277 KB (已減少 47%)")
            print("  3. 考慮使用 WebP 格式")
            return False

    except Exception as e:
        print(f"錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = optimize()
    sys.exit(0 if success else 1)
