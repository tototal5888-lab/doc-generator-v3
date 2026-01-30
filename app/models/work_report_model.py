from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any

@dataclass
class WorkReportEntry:
    """工作報告資料模型"""
    
    # Mapping configuration (Chinese Header -> Attribute Name)
    FIELD_MAPPING = {
        '填單日期': 'fill_date',
        '填單人員': 'filler_name',
        '組別': 'group_name',
        '專案分類Code': 'project_category_code',
        '專案分類': 'project_category',
        '專案Code': 'project_code',
        '專案': 'project',
        '類別': 'category',
        '定義類別': 'defined_category',
        '工作內容': 'work_content',
        '工作時數': 'work_hours',
        '完成百分比': 'completion_percentage',
        '目前百分比': 'current_percentage',
        '差異說明': 'diff_explanation',
        '預計完成日': 'est_completion_date',
        '狀態': 'status',
        '工作報告NOTES文件ID': 'note_doc_id',
        '申請單號': 'app_idx',
        '申請日期': 'app_date',
        '文件狀態': 'doc_status',
        '來源': 'source',
        '資訊處專案': 'it_project',
        '多人專案名稱': 'multi_project_name',
        '專案名稱': 'project_name',
        '專案等級': 'project_level',
        '內容簡述/目的': 'description',
        '電子表單完成日(預計)': 'est_form_completion_date',
        '電子表單完成日(實際)': 'act_form_completion_date',
        '帶入工作確認表': 'import_work_confirm',
        '預計工作天數': 'est_work_days',
        '日期自行輸入': 'date_input_manual',
        '預計開始日期': 'est_start_date',
        '預計完成日期': 'est_end_date',
        '實際開始日期': 'act_start_date',
        '實際完成日期': 'act_end_date',
        '專案目前百分比': 'project_current_percentage',
        '目前狀態': 'current_status',
        '最後統計日期': 'last_stat_date',
        '合計(預計)': 'total_est',
        '合計(實際)': 'total_act',
        '專案NOTES文件ID': 'project_note_id',
        '需求人': 'requester'
    }

    fill_date: Optional[str] = None
    filler_name: Optional[str] = None
    group_name: Optional[str] = None
    project_category_code: Optional[str] = None
    project_category: Optional[str] = None
    project_code: Optional[str] = None
    project: Optional[str] = None
    category: Optional[str] = None
    defined_category: Optional[str] = None
    work_content: Optional[str] = None
    work_hours: Optional[Any] = None
    completion_percentage: Optional[Any] = None
    current_percentage: Optional[Any] = None
    diff_explanation: Optional[str] = None
    est_completion_date: Optional[str] = None
    status: Optional[str] = None
    note_doc_id: Optional[str] = None
    app_idx: Optional[str] = None
    app_date: Optional[str] = None
    doc_status: Optional[str] = None
    source: Optional[str] = None
    it_project: Optional[str] = None
    multi_project_name: Optional[str] = None
    project_name: Optional[str] = None
    project_level: Optional[str] = None
    description: Optional[str] = None
    est_form_completion_date: Optional[str] = None
    act_form_completion_date: Optional[str] = None
    import_work_confirm: Optional[str] = None
    est_work_days: Optional[Any] = None
    date_input_manual: Optional[str] = None
    est_start_date: Optional[str] = None
    est_end_date: Optional[str] = None
    act_start_date: Optional[str] = None
    act_end_date: Optional[str] = None
    project_current_percentage: Optional[Any] = None
    current_status: Optional[str] = None
    last_stat_date: Optional[str] = None
    total_est: Optional[Any] = None
    total_act: Optional[Any] = None
    project_note_id: Optional[str] = None
    requester: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict):
        """從字典創建實例，自動映射欄位名稱"""
        entry = cls()
        # 反轉映射：屬性名 -> 中文欄位名
        reverse_mapping = {v: k for k, v in cls.FIELD_MAPPING.items()}
        
        for attr, field_name in reverse_mapping.items():
            # 嘗試完全匹配
            value = data.get(field_name)
            if value is None:
                # 嘗試查找去除空白的匹配
                for k, v in data.items():
                    if k and str(k).strip() == field_name:
                        value = v
                        break
            
            setattr(entry, attr, value)
        
        # 特殊處理：如果有額外的欄位邏輯可以在這裡添加
        return entry

    @staticmethod
    def generate_sql_ddl(table_name="WORK_REPORTS"):
        """生成 Oracle SQL DDL"""
        columns = [
            "ID NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY",
            "FILL_DATE DATE",
            "FILLER_NAME VARCHAR2(100)",
            "GROUP_NAME VARCHAR2(100)",
            "PROJECT_CATEGORY_CODE VARCHAR2(50)",
            "PROJECT_CATEGORY VARCHAR2(100)",
            "PROJECT_CODE VARCHAR2(50)",
            "PROJECT VARCHAR2(200)",
            "CATEGORY VARCHAR2(100)",
            "DEFINED_CATEGORY VARCHAR2(100)",
            "WORK_CONTENT CLOB",
            "WORK_HOURS NUMBER(10,2)",
            "COMPLETION_PERCENTAGE NUMBER(5,2)",
            "CURRENT_PERCENTAGE NUMBER(5,2)",
            "DIFF_EXPLANATION VARCHAR2(500)",
            "EST_COMPLETION_DATE DATE",
            "STATUS VARCHAR2(50)",
            "NOTE_DOC_ID VARCHAR2(100)",
            "APP_IDX VARCHAR2(50)",
            "APP_DATE DATE",
            "DOC_STATUS VARCHAR2(50)",
            "SOURCE VARCHAR2(50)",
            "IT_PROJECT VARCHAR2(100)",
            "MULTI_PROJECT_NAME VARCHAR2(200)",
            "PROJECT_NAME VARCHAR2(200)",
            "PROJECT_LEVEL VARCHAR2(50)",
            "DESCRIPTION VARCHAR2(4000)",
            "EST_FORM_COMPLETION_DATE DATE",
            "ACT_FORM_COMPLETION_DATE DATE",
            "IMPORT_WORK_CONFIRM VARCHAR2(10)",
            "EST_WORK_DAYS NUMBER(5,1)",
            "DATE_INPUT_MANUAL VARCHAR2(100)",
            "EST_START_DATE DATE",
            "EST_END_DATE DATE",
            "ACT_START_DATE DATE",
            "ACT_END_DATE DATE",
            "PROJECT_CURRENT_PERCENTAGE NUMBER(5,2)",
            "CURRENT_STATUS VARCHAR2(100)",
            "LAST_STAT_DATE DATE",
            "TOTAL_EST NUMBER(10,2)",
            "TOTAL_ACT NUMBER(10,2)",
            "PROJECT_NOTE_ID VARCHAR2(100)",
            "REQUESTER VARCHAR2(100)",
            "CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        ]
        
        ddl = f"CREATE TABLE {table_name} (\n    " + ",\n    ".join(columns) + "\n);"
        
        comments = []
        reverse_mapping = {v: k for k, v in WorkReportEntry.FIELD_MAPPING.items()}
        for attr, ch_name in reverse_mapping.items():
            col_name = attr.upper()
            comments.append(f"COMMENT ON COLUMN {table_name}.{col_name} IS '{ch_name}';")
            
        return ddl + "\n\n" + "\n".join(comments)

    def to_summary_string(self) -> str:
        """轉換為簡報生成用的摘要字串"""
        parts = []
        if self.fill_date: parts.append(f"日期: {self.fill_date}")
        if self.project: parts.append(f"專案: {self.project}")
        if self.work_content: parts.append(f"工作內容: {self.work_content}")
        if self.work_hours: parts.append(f"時數: {self.work_hours}")
        if self.completion_percentage: parts.append(f"進度: {self.completion_percentage}%")
        if self.status: parts.append(f"狀態: {self.status}")
        
        return " | ".join(parts)
