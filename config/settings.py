import os

class Config:
    # 基本配置
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-12345'
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    TEMPLATE_STORAGE_FOLDER = os.path.join(BASE_DIR, 'templates_storage')
    OUTPUT_FOLDER = os.path.join(BASE_DIR, 'output')
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'pptx', 'ppt', 'txt', 'md'}
    OUTPUT_FORMATS = ['docx', 'pptx', 'pdf', 'md']

    # OpenAI 價格配置（每 1M tokens 的價格，單位：美元）
    OPENAI_PRICING = {
        'gpt-4o': {
            'input': 2.50,
            'output': 10.00
        },
        'gpt-4o-mini': {
            'input': 0.15,
            'output': 0.60
        },
        'gpt-4-turbo': {
            'input': 10.00,
            'output': 30.00
        },
        'gpt-4': {
            'input': 30.00,
            'output': 60.00
        },
        'gpt-3.5-turbo': {
            'input': 0.50,
            'output': 1.50
        }
    }

    # 確保目錄存在
    @staticmethod
    def init_app(app):
        for folder in [Config.UPLOAD_FOLDER, Config.TEMPLATE_STORAGE_FOLDER, Config.OUTPUT_FOLDER]:
            if not os.path.exists(folder):
                os.makedirs(folder)
