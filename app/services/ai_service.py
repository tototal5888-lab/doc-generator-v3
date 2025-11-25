import os
import json
import time
import requests
import google.generativeai as genai
from datetime import datetime
from ..utils.helpers import log_cost_to_file

class AIService:
    """AI 服務 - 處理與 LLM 的交互"""
    
    def __init__(self, app_config):
        self.config = app_config
        self.api_config = self.load_api_config()
        self.api_type = self.api_config.get('api_type', 'gemini')

    def load_api_config(self):
        """加載 API 配置 - 優先從環境變數讀取"""
        config_path = os.path.join('config', 'api_config.json')
        config = {}
        
        # 先從 JSON 文件讀取
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except:
                config = {}
        
        # 環境變數優先級更高，會覆蓋 JSON 文件中的配置
        if os.environ.get('GEMINI_API_KEY'):
            config['gemini_api_key'] = os.environ.get('GEMINI_API_KEY')
        if os.environ.get('OPENAI_API_KEY'):
            config['openai_api_key'] = os.environ.get('OPENAI_API_KEY')
        if os.environ.get('API_TYPE'):
            config['api_type'] = os.environ.get('API_TYPE')
        if os.environ.get('OPENAI_MODEL'):
            config['openai_model'] = os.environ.get('OPENAI_MODEL')
        
        return config

    def save_api_config(self, config):
        """保存 API 配置"""
        config_path = os.path.join('config', 'api_config.json')
        os.makedirs('config', exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        self.api_config = config
        self.api_type = config.get('api_type', 'gemini')

    def call_gemini_api(self, prompt):
        """調用 Gemini API（帶重試機制）"""
        api_key = self.api_config.get('gemini_api_key')
        if not api_key:
            raise Exception("未配置 Gemini API Key")

        genai.configure(api_key=api_key)
        
        # 使用 Gemini 2.0 Flash (速度快且免費額度高)
        model_name = self.api_config.get('gemini_model', 'gemini-2.0-flash-exp')
        
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
        )

        max_retries = 3
        for attempt in range(max_retries):
            try:
                chat_session = model.start_chat(history=[])
                response = chat_session.send_message(prompt)
                
                # Gemini 目前免費，或者需要從 response.usage_metadata 獲取 token 數
                # 這裡簡單返回 0 成本
                usage_info = {
                    "model": model_name,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cost": 0.0
                }
                return response.text, usage_info
            except Exception as e:
                if attempt == max_retries - 1:
                    raise Exception(f"Gemini API 調用失敗 (重試 {max_retries} 次後): {str(e)}")
                time.sleep(2) # 等待後重試

    def call_openai_api(self, prompt):
        """調用 OpenAI API（帶成本追蹤）"""
        api_key = self.api_config.get('openai_api_key')
        if not api_key:
            raise Exception("未配置 OpenAI API Key")

        model = self.api_config.get('openai_model')
        if not model:
            model = 'gpt-4o-mini'
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一個專業的文檔生成助手，擅長撰寫各種技術文檔、報告和 SOP。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7
        }

        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenAI API Error: {response.text}")
                
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # 計算成本
            usage = result.get('usage', {})
            input_tokens = usage.get('prompt_tokens', 0)
            output_tokens = usage.get('completion_tokens', 0)
            
            pricing = self.config['OPENAI_PRICING'].get(model, {'input': 0, 'output': 0})
            cost = (input_tokens / 1000000 * pricing['input']) + \
                   (output_tokens / 1000000 * pricing['output'])
            
            # 記錄成本
            log_cost_to_file(model, input_tokens, output_tokens, cost)
            
            usage_info = {
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": cost
            }
            
            return content, usage_info
            
        except Exception as e:
            raise Exception(f"OpenAI API 調用失敗: {str(e)}")

    def call_mock_api(self, prompt):
        """調用模擬 API (不消耗額度)"""
        time.sleep(1) # 模擬延遲
        
        content = """# 模擬生成文檔

這是一份由模擬 AI 生成的文檔內容。

## 1. 簡介
本系統是一個高效的文件生成工具...

## 2. 功能
- 支持多種格式
- AI 智能生成
- 模擬模式測試

## 3. 結論
模擬模式運行正常。
"""
        usage_info = {
            "model": "mock-model",
            "input_tokens": len(prompt),
            "output_tokens": len(content),
            "cost": 0.0
        }
        return content, usage_info

    def generate_content(self, prompt):
        """生成內容的主入口"""
        api_config = self.load_api_config()
        api_type = api_config.get('api_type', 'gemini')
        
        if api_type == 'gemini':
            return self.call_gemini_api(prompt)
        elif api_type == 'openai':
            return self.call_openai_api(prompt)
        elif api_type == 'mock':
            return self.call_mock_api(prompt)
        else:
            raise ValueError(f"不支持的 API 類型: {api_type}")
