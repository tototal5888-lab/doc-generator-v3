from flask import Flask
from flask_cors import CORS
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static') # 假設 static 在根目錄，雖然目前可能沒用到
    
    app.config.from_object(config_class)
    
    # 初始化擴展
    CORS(app)
    
    # 初始化配置目錄
    config_class.init_app(app)
    
    # 註冊藍圖
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)
    
    return app
