import sys
print(f"Python 版本: {sys.version}\n")

print("檢查核心依賴：")
print("-" * 50)

try:
    import flask
    print(f"✅ Flask: {flask.__version__}")
except: print("❌ Flask")

try:
    import flask_cors
    print(f"✅ Flask-CORS: 已安裝")
except: print("❌ Flask-CORS")

try:
    import docx
    print(f"✅ python-docx: 已安裝")
except: print("❌ python-docx")

try:
    import pptx
    print(f"✅ python-pptx: 已安裝")
except: print("❌ python-pptx")

try:
    import requests
    print(f"✅ requests: {requests.__version__}")
except: print("❌ requests")

try:
    import reportlab
    print(f"✅ reportlab: 已安裝 (PDF 生成功能可用)")
except: print("❌ reportlab")

try:
    import markdown
    print(f"✅ markdown: 已安裝")
except: print("❌ markdown")

print("\n可選依賴：")
print("-" * 50)

try:
    import fitz
    print(f"✅ PyMuPDF (PDF 模板讀取)")
except:
    print(f"⚠️  PyMuPDF 未安裝 (PDF 模板功能不可用)")

print("\n" + "=" * 50)
print("🎉 核心功能完整，可以啟動應用！")
print("\n下一步: python app_v3.py")