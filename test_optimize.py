import requests
import json

url = 'http://127.0.0.1:5000/api/optimize-requirements'
data = {
    "requirements": "測試需求",
    "doc_type": "sop"
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:200]}...")
except Exception as e:
    print(f"Error: {e}")
