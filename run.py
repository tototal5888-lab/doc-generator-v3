from app import create_app

app = create_app()

if __name__ == '__main__':
    # host='0.0.0.0' 允許從網路訪問
    # 可以通過 http://127.0.0.1:5000 或 http://10.1.54.199:5000 訪問
    app.run(host='0.0.0.0', port=5000, debug=True)
