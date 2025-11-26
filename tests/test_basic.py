import unittest
import sys
import os

# 添加項目根目錄到 path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app

class BasicTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()

    def test_index(self):
        """測試首頁是否可以訪問"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_config_api(self):
        """測試配置 API"""
        response = self.client.get('/api/config')
        self.assertEqual(response.status_code, 200)

    def test_template_delete(self):
        """測試模板刪除"""
        # 1. 先創建一個測試文件
        folder = self.app.config['TEMPLATE_STORAGE_FOLDER']
        filename = 'test_delete.txt'
        file_path = os.path.join(folder, filename)
        with open(file_path, 'w') as f:
            f.write('test content')
            
        # 2. 調用刪除 API
        response = self.client.delete(f'/api/delete_template/{filename}')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(os.path.exists(file_path))

    def test_template_list_format(self):
        """測試模板列表格式"""
        # 1. 創建測試文件
        folder = self.app.config['TEMPLATE_STORAGE_FOLDER']
        filename = 'test_list.txt'
        file_path = os.path.join(folder, filename)
        with open(file_path, 'w') as f:
            f.write('test content')
            
        # 2. 獲取列表
        response = self.client.get('/api/templates')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertTrue(len(data) > 0)
        
        # 3. 驗證格式
        item = next((x for x in data if x['filename'] == filename), None)
        self.assertIsNotNone(item)
        self.assertIn('filename', item)
        self.assertIn('type', item)
        self.assertIn('size', item)
        self.assertIn('modified', item)
        self.assertEqual(item['type'], 'TXT')
        
        # 清理
        os.remove(file_path)

    def test_generate_params(self):
        """測試生成接口參數驗證"""
        # 測試缺少參數
        response = self.client.post('/api/generate', json={})
        self.assertEqual(response.status_code, 400)
        
        # 測試參數名稱是否正確 (模擬前端請求)
        # 注意：這裡不測試實際生成，因為需要 API Key，我們只測試參數驗證通過後的行為
        # 如果參數正確但沒有 API Key，應該會進入生成流程然後報錯(500)，而不是 400
        
        # 1. 創建一個臨時模板文件
        folder = self.app.config['TEMPLATE_STORAGE_FOLDER']
        filename = 'test_gen.txt'
        file_path = os.path.join(folder, filename)
        with open(file_path, 'w') as f:
            f.write('test content')

        response = self.client.post('/api/generate', json={
            "doc_type": "sop",
            "template": filename, # 前端使用 template
            "requirements": "test requirements",
            "output_format": "md"
        })
        
        # 如果返回 500，說明參數驗證通過了（進入了生成邏輯但失敗了）
        # 如果返回 400，說明參數驗證沒通過
        # 注意：現在我們修復了 API 調用，如果配置正確，這裡可能會返回 200
        # 所以我們只斷言不是 400
        self.assertNotEqual(response.status_code, 400)
        
        if response.status_code == 200:
            self.assertTrue(response.json.get('success'))
        
        # 清理
        os.remove(file_path)

    def test_ai_service_logic(self):
        """測試 AI Service 邏輯"""
        from app.services.ai_service import AIService
        from unittest.mock import MagicMock, patch
        
        # 模擬 Config
        mock_config = {
            'OPENAI_PRICING': {
                'gpt-4o': {'input': 5.0, 'output': 15.0}
            }
        }
        
        service = AIService(mock_config)
        
        # 測試 1: 默認模型
        # 模擬 api_config
        service.api_config = {
            'openai_api_key': 'test_key',
            'openai_model': '' # 空字符串
        }
        
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'choices': [{'message': {'content': 'test content'}}],
                'usage': {'prompt_tokens': 10, 'completion_tokens': 20}
            }
            mock_post.return_value = mock_response
            
            # 調用
            content, usage = service.call_openai_api('test prompt')
            
            # 驗證
            self.assertEqual(content, 'test content')
            
            # 驗證請求中使用了默認模型 gpt-4o-mini
            call_args = mock_post.call_args
            self.assertEqual(call_args[1]['json']['model'], 'gpt-4o-mini')

    def test_generated_documents_list(self):
        """測試已生成文檔列表"""
        # 1. 創建一個模擬的生成文件
        folder = self.app.config['OUTPUT_FOLDER']
        filename = 'generated_test_doc.docx'
        file_path = os.path.join(folder, filename)
        with open(file_path, 'w') as f:
            f.write('test content')
            
        # 2. 調用 API
        response = self.client.get('/api/generated_documents')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertTrue(len(data) > 0)
        
        # 3. 驗證格式
        item = next((x for x in data if x['filename'] == filename), None)
        self.assertIsNotNone(item)
        self.assertIn('filename', item)
        self.assertIn('format', item)
        self.assertIn('size', item)
        self.assertIn('created', item)
        self.assertEqual(item['format'], 'DOCX')
        
        # 清理
        os.remove(file_path)

    def test_generate_response_structure(self):
        """測試生成接口響應結構"""
        from unittest.mock import MagicMock, patch
        
        # 1. 創建臨時模板
        folder = self.app.config['TEMPLATE_STORAGE_FOLDER']
        filename = 'test_gen_struct.txt'
        file_path = os.path.join(folder, filename)
        with open(file_path, 'w') as f:
            f.write('test content')
            
        # 2. 模擬 AI Service
        with patch('app.services.ai_service.AIService.generate_content') as mock_generate:
            # 模擬返回 (content, usage_info)
            mock_generate.return_value = ("# Generated Content", {
                "model": "mock-model",
                "input_tokens": 10,
                "output_tokens": 20,
                "cost": 0.001
            })
            
            # 3. 調用生成 API
            response = self.client.post('/api/generate', json={
                "doc_type": "sop",
                "template": filename,
                "requirements": "test req",
                "output_format": "md"
            })
            
            self.assertEqual(response.status_code, 200)
            data = response.json
            
            # 4. 驗證響應字段
            self.assertTrue(data.get('success'))
            self.assertIn('filename', data)
            self.assertIn('format', data)
            self.assertIn('download_url', data)
            self.assertIn('usage', data) # 驗證 usage 字段
            self.assertEqual(data['format'], 'md')
            self.assertTrue(data['filename'].endswith('.md'))
            
            # 驗證 usage 內容
            usage = data['usage']
            self.assertIn('model', usage)
            self.assertIn('cost', usage)
            
            # 驗證 download_url 格式
            self.assertTrue(data['download_url'].startswith('/api/download/'))
            
        # 清理
        os.remove(file_path)

    def test_download_file(self):
        """測試文件下載"""
        # 1. 創建測試文件
        folder = self.app.config['OUTPUT_FOLDER']
        filename = 'test_download.txt'
        file_path = os.path.join(folder, filename)
        with open(file_path, 'w') as f:
            f.write('test content')
            
        try:
            # 2. 調用下載 API
            response = self.client.get(f'/api/download/{filename}')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data.decode(), 'test content')
        finally:
            # 清理 - 確保文件關閉後再刪除
            response.close()
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except PermissionError:
                    pass # Windows 上可能會有鎖定問題，忽略

    def test_mock_generation(self):
        """測試模擬生成模式"""
        # 1. 確保配置為 mock
        from app.services.ai_service import AIService
        from unittest.mock import patch
        
        # 2. 創建臨時模板
        folder = self.app.config['TEMPLATE_STORAGE_FOLDER']
        filename = 'test_mock.txt'
        file_path = os.path.join(folder, filename)
        with open(file_path, 'w') as f:
            f.write('test content')
            
        try:
            # 3. 調用生成 API
            with patch('app.services.ai_service.AIService.load_api_config') as mock_load:
                mock_load.return_value = {'api_type': 'mock'}
                
                response = self.client.post('/api/generate', json={
                    "doc_type": "sop",
                    "template": filename,
                    "requirements": "test req",
                    "output_format": "md"
                })
                
                self.assertEqual(response.status_code, 200)
                data = response.json
                self.assertTrue(data.get('success'))
                self.assertEqual(data['usage']['model'], 'mock-model')
                self.assertIn('模擬生成文檔', data['preview'])
        finally:
            # 清理
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except PermissionError:
                    pass

if __name__ == '__main__':
    unittest.main()
