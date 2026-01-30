"""
簡單測試 TextParser 功能 (不載入整個 app)
"""

import re


class TextParser:
    """文字檔解析器 - 從文字內容中識別並提取填單人員資訊"""
    
    # 可能的填單人員欄位關鍵字
    USER_FIELD_KEYWORDS = ['填單人員', '填單人', '需求人', '負責人', '人員', '姓名', '申請人']
    
    @staticmethod
    def find_user_markers(text):
        """在文字中尋找所有人員標記"""
        markers = []
        
        for keyword in TextParser.USER_FIELD_KEYWORDS:
            pattern = rf'{keyword}\s*[:：　\s]+([A-Za-z\u4e00-\u9fa50-9]+)'
            
            for match in re.finditer(pattern, text):
                user_name = match.group(1).strip()
                if user_name:
                    markers.append({
                        'user': user_name,
                        'position': match.start(),
                        'keyword': keyword,
                        'full_match': match.group(0)
                    })
                    print(f"[DEBUG] 找到人員標記: '{match.group(0)}' -> 人員: '{user_name}' (關鍵字: {keyword})")
        
        markers.sort(key=lambda x: x['position'])
        return markers
    
    @staticmethod
    def split_by_user(text, markers):
        """根據人員標記將文字分段"""
        if not markers:
            return {}
        
        data_by_user = {}
        
        for i, marker in enumerate(markers):
            user_name = marker['user']
            start_pos = marker['position']
            
            if i + 1 < len(markers):
                end_pos = markers[i + 1]['position']
            else:
                end_pos = len(text)
            
            user_text = text[start_pos:end_pos].strip()
            
            if user_name in data_by_user:
                data_by_user[user_name] += f"\n\n---\n\n{user_text}"
            else:
                data_by_user[user_name] = user_text
        
        return data_by_user
    
    @staticmethod
    def parse_work_report_text(text):
        """解析工作報告文字檔"""
        if not text or not isinstance(text, str):
            return {
                'has_multiple_users': False,
                'users': [],
                'data_by_user': {},
                'all_data': text or ''
            }
        
        markers = TextParser.find_user_markers(text)
        
        if not markers:
            print("[INFO] 文字檔中未找到人員標記，視為單一文件")
            return {
                'has_multiple_users': False,
                'users': [],
                'data_by_user': {},
                'all_data': text
            }
        
        users = []
        seen = set()
        for marker in markers:
            user = marker['user']
            if user not in seen:
                users.append(user)
                seen.add(user)
        
        has_multiple_users = len(users) > 1
        data_by_user = TextParser.split_by_user(text, markers)
        
        print(f"[DEBUG] 文字解析完成: has_multiple_users={has_multiple_users}")
        print(f"[DEBUG] 識別到的人員列表 ({len(users)}位): {users}")
        
        return {
            'has_multiple_users': has_multiple_users,
            'users': users,
            'data_by_user': data_by_user,
            'all_data': text
        }


def test_single_user():
    print("\n" + "="*60)
    print("測試案例 1：單人員文字檔")
    print("="*60)
    
    with open('test_single_user.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    result = TextParser.parse_work_report_text(text)
    
    print(f"\n結果:")
    print(f"  has_multiple_users: {result['has_multiple_users']}")
    print(f"  識別到的人員數: {len(result['users'])}")
    print(f"  人員列表: {result['users']}")
    
    assert result['has_multiple_users'] == False, "應該是單人員"
    assert len(result['users']) == 1, "應該只有一位人員"
    assert '王小明' in result['users'], "應該包含王小明"
    
    print("\n✅ 測試通過！")


def test_multiple_users():
    print("\n" + "="*60)
    print("測試案例 2：多人員文字檔")
    print("="*60)
    
    with open('test_multiple_users.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    result = TextParser.parse_work_report_text(text)
    
    print(f"\n結果:")
    print(f"  has_multiple_users: {result['has_multiple_users']}")
    print(f"  識別到的人員數: {len(result['users'])}")
    print(f"  人員列表: {result['users']}")
    
    assert result['has_multiple_users'] == True, "應該是多人員"
    assert len(result['users']) == 3, "應該有三位人員"
    assert '王小明' in result['users'], "應該包含王小明"
    assert '李大華' in result['users'], "應該包含李大華"
    assert '張三' in result['users'], "應該包含張三"
    
    for user in result['users']:
        assert user in result['data_by_user'], f"{user} 應該在 data_by_user 中"
        user_data = result['data_by_user'][user]
        assert user in user_data, f"{user} 的資料應該包含其名字"
        print(f"\n  {user} 的資料長度: {len(user_data)} 字元")
    
    print("\n✅ 測試通過！")


def test_mixed_format():
    print("\n" + "="*60)
    print("測試案例 3：混合格式文字檔")
    print("="*60)
    
    with open('test_mixed_format.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    result = TextParser.parse_work_report_text(text)
    
    print(f"\n結果:")
    print(f"  has_multiple_users: {result['has_multiple_users']}")
    print(f"  識別到的人員數: {len(result['users'])}")
    print(f"  人員列表: {result['users']}")
    
    assert result['has_multiple_users'] == True, "應該是多人員"
    assert len(result['users']) == 2, "應該有兩位人員"
    assert '王小明' in result['users'], "應該包含王小明"
    assert '李大華' in result['users'], "應該包含李大華"
    
    print("\n✅ 測試通過！")


if __name__ == '__main__':
    try:
        test_single_user()
        test_multiple_users()
        test_mixed_format()
        
        print("\n" + "="*60)
        print("🎉 所有測試通過！")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n❌ 測試失敗: {e}")
        import sys
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        import sys
        sys.exit(1)
