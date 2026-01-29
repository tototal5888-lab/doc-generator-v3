"""
文字檔解析器 - 專門用於工作報告的人員資訊提取和分組
"""

import re


class TextParser:
    """文字檔解析器 - 從文字內容中識別並提取填單人員資訊"""
    
    # 可能的填單人員欄位關鍵字
    USER_FIELD_KEYWORDS = ['填單人員', '填單人', '需求人', '負責人', '人員', '姓名', '申請人']
    
    @staticmethod
    def find_user_markers(text):
        """在文字中尋找所有人員標記
        
        Args:
            text: 要解析的文字內容
            
        Returns:
            list: [(user_name, start_pos, keyword), ...]
        """
        markers = []
        
        # 建立正則表達式模式
        # 支援：「填單人員：王小明」、「負責人: 李大華」、「姓名　張三」
        for keyword in TextParser.USER_FIELD_KEYWORDS:
            # 匹配模式：關鍵字 + (冒號/空格/全形空格) + 人名
            # 人名：中文字、英文字母、數字，1-20 字元
            pattern = rf'{keyword}\s*[:：　\s]+([A-Za-z\u4e00-\u9fa50-9]+)'
            
            for match in re.finditer(pattern, text):
                user_name = match.group(1).strip()
                if user_name:  # 確保不是空字串
                    markers.append({
                        'user': user_name,
                        'position': match.start(),
                        'keyword': keyword,
                        'full_match': match.group(0)
                    })
                    print(f"[DEBUG] 找到人員標記: '{match.group(0)}' -> 人員: '{user_name}' (關鍵字: {keyword})")
        
        # 按位置排序
        markers.sort(key=lambda x: x['position'])
        return markers
    
    @staticmethod
    def split_by_user(text, markers):
        """根據人員標記將文字分段
        
        Args:
            text: 要分割的文字
            markers: find_user_markers() 的返回值
            
        Returns:
            dict: {user_name: user_text, ...}
        """
        if not markers:
            return {}
        
        data_by_user = {}
        
        for i, marker in enumerate(markers):
            user_name = marker['user']
            start_pos = marker['position']
            
            # 確定結束位置（到下一個人員標記之前，或到文字結尾）
            if i + 1 < len(markers):
                end_pos = markers[i + 1]['position']
            else:
                end_pos = len(text)
            
            # 提取該人員的文字段落
            user_text = text[start_pos:end_pos].strip()
            
            # 如果同一人員出現多次，合併內容
            if user_name in data_by_user:
                data_by_user[user_name] += f"\n\n---\n\n{user_text}"
            else:
                data_by_user[user_name] = user_text
        
        return data_by_user
    
    @staticmethod
    def parse_work_report_text(text):
        """解析工作報告文字檔，返回結構化資料
        
        Args:
            text: 文字內容
            
        Returns:
            dict: {
                'has_multiple_users': bool,
                'users': list,
                'data_by_user': dict,
                'all_data': str
            }
        """
        if not text or not isinstance(text, str):
            return {
                'has_multiple_users': False,
                'users': [],
                'data_by_user': {},
                'all_data': text or ''
            }
        
        # 尋找所有人員標記
        markers = TextParser.find_user_markers(text)
        
        if not markers:
            # 沒有找到人員標記，視為單一文件
            print("[INFO] 文字檔中未找到人員標記，視為單一文件")
            return {
                'has_multiple_users': False,
                'users': [],
                'data_by_user': {},
                'all_data': text
            }
        
        # 收集所有唯一的人員名稱
        users = []
        seen = set()
        for marker in markers:
            user = marker['user']
            if user not in seen:
                users.append(user)
                seen.add(user)
        
        has_multiple_users = len(users) > 1
        
        # 按人員分割文字
        data_by_user = TextParser.split_by_user(text, markers)
        
        print(f"[DEBUG] 文字解析完成: has_multiple_users={has_multiple_users}")
        print(f"[DEBUG] 識別到的人員列表 ({len(users)}位): {users}")
        
        return {
            'has_multiple_users': has_multiple_users,
            'users': users,
            'data_by_user': data_by_user,
            'all_data': text
        }
