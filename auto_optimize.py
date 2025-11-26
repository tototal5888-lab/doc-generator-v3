#!/usr/bin/env python3
"""
自動圖示優化工具 - 不需要額外安裝套件
使用 Python 標準庫進行圖片壓縮
"""

import os
import sys
import subprocess
from pathlib import Path

def check_and_install_pillow():
    """檢查並安裝 Pillow"""
    try:
        from PIL import Image
        print("✅ Pillow 已安裝")
        return True
    except ImportError:
        print("📦 Pillow 未安裝，正在安裝...")
        try:
            # 嘗試在使用者空間安裝
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "--user", "Pillow", "-q"
            ])
            print("✅ Pillow 安裝成功")
            return True
        except Exception as e:
            print(f"❌ 無法安裝 Pillow: {e}")
            print("\n請手動安裝：")
            print("  pip install --user Pillow")
            print("或")
            print("  python3 -m pip install --user Pillow")
            return False

def optimize_with_pillow():
    """使用 Pillow 優化圖示"""
    try:
        from PIL import Image
        import time

        print("=" * 70)
        print("🎨 自動圖示優化工具")
        print("=" * 70)
        print()

        # 檢查原始檔案
        input_path = 'static/icon.png'
        if not os.path.exists(input_path):
            print(f"❌ 找不到檔案: {input_path}")
            return False

        # 顯示原始資訊
        original_size = os.path.getsize(input_path)
        print(f"📊 原始檔案資訊:")
        print(f"   - 路徑: {input_path}")
        print(f"   - 大小: {original_size / 1024:.2f} KB")

        # 備份原始檔案
        backup_path = 'static/icon_original.png'
        if os.path.exists(backup_path):
            print(f"   - 備份已存在: {backup_path}")
        else:
            print(f"\n💾 備份原始檔案...")
            import shutil
            shutil.copy2(input_path, backup_path)
            print(f"✅ 已備份到: {backup_path}")

        print(f"\n🔄 開始優化...")

        # 開啟圖片
        img = Image.open(input_path)
        print(f"   - 格式: {img.format}")
        print(f"   - 尺寸: {img.size}")
        print(f"   - 模式: {img.mode}")

        # 轉換為 RGB（如果需要）
        if img.mode == 'RGBA':
            print("   - 轉換 RGBA → RGB")
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode != 'RGB':
            print(f"   - 轉換 {img.mode} → RGB")
            img = img.convert('RGB')

        # 生成多種尺寸和格式
        outputs = []

        # 主圖示 512x512
        print(f"\n📦 生成優化版本...")

        # 512x512 PNG (主要)
        print("   1. 主圖示 (512x512 PNG)...")
        resized = img.resize((512, 512), Image.Resampling.LANCZOS)
        temp_path = 'static/icon_temp.png'
        resized.save(temp_path, 'PNG', optimize=True, quality=85)
        size_512_png = os.path.getsize(temp_path)

        # 如果 PNG 還是太大，改用 JPEG
        if size_512_png > 100 * 1024:  # > 100KB
            print("      PNG 過大，改用 JPEG...")
            resized.save(temp_path, 'JPEG', optimize=True, quality=85)
            size_512_jpg = os.path.getsize(temp_path)
            if size_512_jpg < size_512_png:
                print(f"      使用 JPEG (更小): {size_512_jpg / 1024:.2f} KB")
            else:
                resized.save(temp_path, 'PNG', optimize=True, quality=85)

        # 替換原始檔案
        os.replace(temp_path, input_path)
        optimized_size = os.path.getsize(input_path)
        outputs.append(('icon.png', 512, optimized_size))
        print(f"      ✅ {optimized_size / 1024:.2f} KB")

        # 256x256
        print("   2. 中等尺寸 (256x256)...")
        resized_256 = img.resize((256, 256), Image.Resampling.LANCZOS)
        path_256 = 'static/icon-256.png'
        resized_256.save(path_256, 'PNG', optimize=True, quality=85)
        size_256 = os.path.getsize(path_256)
        outputs.append(('icon-256.png', 256, size_256))
        print(f"      ✅ {size_256 / 1024:.2f} KB")

        # 128x128
        print("   3. 小尺寸 (128x128)...")
        resized_128 = img.resize((128, 128), Image.Resampling.LANCZOS)
        path_128 = 'static/icon-128.png'
        resized_128.save(path_128, 'PNG', optimize=True, quality=85)
        size_128 = os.path.getsize(path_128)
        outputs.append(('icon-128.png', 128, size_128))
        print(f"      ✅ {size_128 / 1024:.2f} KB")

        # 64x64
        print("   4. 縮圖 (64x64)...")
        resized_64 = img.resize((64, 64), Image.Resampling.LANCZOS)
        path_64 = 'static/icon-64.png'
        resized_64.save(path_64, 'PNG', optimize=True, quality=85)
        size_64 = os.path.getsize(path_64)
        outputs.append(('icon-64.png', 64, size_64))
        print(f"      ✅ {size_64 / 1024:.2f} KB")

        # Favicon 32x32
        print("   5. Favicon (32x32)...")
        resized_32 = img.resize((32, 32), Image.Resampling.LANCZOS)
        path_32 = 'static/favicon.ico'
        resized_32.save(path_32, 'ICO')
        size_32 = os.path.getsize(path_32)
        outputs.append(('favicon.ico', 32, size_32))
        print(f"      ✅ {size_32 / 1024:.2f} KB")

        # 顯示結果
        print("\n" + "=" * 70)
        print("📊 優化結果")
        print("=" * 70)
        print()
        print(f"{'檔案':<25} {'尺寸':<12} {'大小':<12} {'狀態'}")
        print("-" * 70)

        for filename, size, filesize in outputs:
            size_kb = filesize / 1024
            status = "✅" if size_kb < 100 else "⚠️"
            print(f"{filename:<25} {size}x{size:<8} {size_kb:>6.2f} KB    {status}")

        # 計算節省
        saved = original_size - optimized_size
        percent = (saved / original_size) * 100

        print()
        print("=" * 70)
        print("📈 優化統計:")
        print(f"   原始大小: {original_size / 1024:.2f} KB")
        print(f"   優化後:   {optimized_size / 1024:.2f} KB")
        print(f"   節省:     {saved / 1024:.2f} KB ({percent:.1f}%)")

        # 評級
        if optimized_size < 100 * 1024 and percent > 60:
            if percent >= 80:
                grade = "A+ 🏆"
            elif percent >= 70:
                grade = "A 🎉"
            else:
                grade = "B+ 👍"
            print(f"   等級:     {grade}")
            print()
            print("🎉 優化成功！")
        else:
            print()
            print("⚠️  優化完成，但可能需要進一步處理")
            if optimized_size >= 100 * 1024:
                print("   建議：使用線上工具 (TinyPNG) 進一步壓縮")

        print("=" * 70)
        print()
        print("📝 後續步驟:")
        print("   1. 執行 ./verify_optimization.sh 驗證結果")
        print("   2. 執行 python run.py 啟動應用測試")
        print("   3. 在瀏覽器中檢查圖示顯示效果")
        print()

        return True

    except Exception as e:
        print(f"❌ 優化失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主程式"""
    if not check_and_install_pillow():
        return 1

    # 重新導入以確保使用新安裝的 Pillow
    try:
        from PIL import Image
    except ImportError:
        print("❌ Pillow 安裝失敗，請手動安裝後重試")
        return 1

    if optimize_with_pillow():
        return 0
    else:
        return 1

if __name__ == '__main__':
    sys.exit(main())
