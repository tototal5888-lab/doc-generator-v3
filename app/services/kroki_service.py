"""
Kroki 服務 - 透過 Kroki API 將 Mermaid code 轉換為 PNG 圖片
"""
import os
import requests
from datetime import datetime


class KrokiService:
    """Kroki 服務 - 負責生成 Mermaid code 和轉換為 PNG"""
    
    KROKI_URL = "https://kroki.io/mermaid/png"
    
    def __init__(self, output_dir: str):
        """
        初始化 Kroki 服務
        
        Args:
            output_dir: 輸出目錄路徑
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_mermaid_prompt(self, description: str) -> str:
        """
        生成讓 AI 產生 Mermaid code 的 prompt
        
        Args:
            description: 用戶的流程描述
            
        Returns:
            完整的 prompt
        """
        return f"""請根據以下流程描述，生成 Mermaid flowchart 語法。

**要求：**
1. 使用 `flowchart TD` (由上到下) 或 `flowchart LR` (由左到右) 格式
2. 節點使用中文標籤
3. 條件判斷使用菱形 {{}}
4. 開始/結束使用圓角框 ([])
5. 一般步驟使用方框 []
6. 只輸出 Mermaid code，不要其他說明文字
7. 確保語法正確，可以被 Kroki 解析

**流程描述：**
{description}

**輸出 Mermaid code：**
```mermaid
"""

    def convert_mermaid_to_png(self, mermaid_code: str) -> tuple[bytes, str]:
        """
        調用 Kroki API 將 Mermaid code 轉換為 PNG
        
        Args:
            mermaid_code: Mermaid 語法代碼
            
        Returns:
            tuple: (PNG 二進位資料, 錯誤訊息)
        """
        try:
            # 清理 mermaid code（移除可能的 markdown 包裝）
            clean_code = mermaid_code.strip()
            if clean_code.startswith("```mermaid"):
                clean_code = clean_code[len("```mermaid"):].strip()
            if clean_code.startswith("```"):
                clean_code = clean_code[3:].strip()
            if clean_code.endswith("```"):
                clean_code = clean_code[:-3].strip()
            
            response = requests.post(
                self.KROKI_URL,
                data=clean_code.encode("utf-8"),
                headers={"Content-Type": "text/plain"},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.content, None
            else:
                return None, f"Kroki API 錯誤: HTTP {response.status_code} - {response.text}"
                
        except requests.Timeout:
            return None, "Kroki API 請求超時"
        except requests.RequestException as e:
            return None, f"Kroki API 請求失敗: {str(e)}"
    
    def save_png(self, png_data: bytes, filename: str = None) -> str:
        """
        保存 PNG 圖片到輸出目錄
        
        Args:
            png_data: PNG 二進位資料
            filename: 可選的檔名，若未提供則自動生成
            
        Returns:
            保存的檔案路徑
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"flowchart_{timestamp}.png"
        
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "wb") as f:
            f.write(png_data)
        
        return filepath
    
    def generate_flowchart(self, mermaid_code: str) -> dict:
        """
        從 Mermaid code 生成流程圖 PNG
        
        Args:
            mermaid_code: Mermaid 語法代碼
            
        Returns:
            dict: {
                'success': bool,
                'filename': str (如果成功),
                'filepath': str (如果成功),
                'error': str (如果失敗)
            }
        """
        # 轉換為 PNG
        png_data, error = self.convert_mermaid_to_png(mermaid_code)
        
        if error:
            return {
                'success': False,
                'error': error
            }
        
        # 保存 PNG
        filepath = self.save_png(png_data)
        filename = os.path.basename(filepath)
        
        return {
            'success': True,
            'filename': filename,
            'filepath': filepath
        }
