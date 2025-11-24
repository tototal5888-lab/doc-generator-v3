import os
import re
from docx import Document
from pptx import Presentation
from pptx.util import Inches, Pt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class FormatConverter:
    """格式轉換器 - 將 Markdown 轉換為各種輸出格式"""

    @staticmethod
    def markdown_to_docx(content, doc_config):
        """將Markdown轉換為DOCX"""
        doc = Document()
        
        # 添加標題
        doc.add_heading(doc_config.get('title', '生成的文檔'), 0)
        
        # 處理內容
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('# '):
                doc.add_heading(line[2:], 1)
            elif line.startswith('## '):
                doc.add_heading(line[3:], 2)
            elif line.startswith('### '):
                doc.add_heading(line[4:], 3)
            elif line.startswith('- ') or line.startswith('* '):
                doc.add_paragraph(line[2:], style='List Bullet')
            elif re.match(r'^\d+\. ', line):
                doc.add_paragraph(line.split('. ', 1)[1], style='List Number')
            else:
                doc.add_paragraph(line)
                
        return doc

    @staticmethod
    def markdown_to_pptx(content, doc_config, image_folder=None):
        """
        將Markdown轉換為PPTX
        
        Args:
            content: Markdown 內容
            doc_config: 文檔配置
            image_folder: 圖片文件夾路徑（可選）
        """
        prs = Presentation()
        
        # 標題頁
        title_slide_layout = prs.slide_layouts[0]
        slide = prs.slides.add_slide(title_slide_layout)
        title = slide.shapes.title
        subtitle = slide.placeholders[1]
        
        title.text = doc_config.get('title', '生成的演示文稿')
        subtitle.text = "由 AI 自動生成"
        
        # 內容頁
        bullet_slide_layout = prs.slide_layouts[1]
        blank_slide_layout = prs.slide_layouts[6]  # 空白版面用於插入圖片
        
        current_slide = None
        body_shape = None
        tf = None
        
        # 圖片標記的正則表達式：支持多種格式
        # 格式1: [圖片 1-1: 來自投影片 1]
        # 格式2: - 圖片 1-1: 來自投影片 1
        image_pattern = re.compile(r'[-\[]?\s*圖片\s+(\d+)-(\d+)(?::\s*來自投影片\s*\d+)?[\]]?')
        
        lines = content.split('\n')
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            # 檢查是否為圖片標記
            image_match = image_pattern.search(line_stripped)
            if image_match and image_folder:
                slide_num = image_match.group(1)
                img_num = image_match.group(2)
                
                # 構建圖片文件名
                image_filename = f"slide_{slide_num}_image_{img_num}"
                
                # 查找匹配的圖片文件（可能有不同擴展名）
                image_path = None
                for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                    potential_path = os.path.join(image_folder, image_filename + ext)
                    if os.path.exists(potential_path):
                        image_path = potential_path
                        break
                
                # 如果找到圖片，插入到投影片中
                if image_path:
                    # 如果當前沒有投影片，創建一個帶標題的投影片
                    if not current_slide:
                        current_slide = prs.slides.add_slide(bullet_slide_layout)
                        shapes = current_slide.shapes
                        title_shape = shapes.title
                        title_shape.text = "圖片內容"
                        body_shape = shapes.placeholders[1]
                        tf = body_shape.text_frame
                    
                    # 在當前投影片中插入圖片（放在右側或下方）
                    left = Inches(5.5)  # 靠右放置
                    top = Inches(1.5)
                    width = Inches(3.5)  # 設定寬度，高度自動調整
                    
                    try:
                        current_slide.shapes.add_picture(image_path, left, top, width=width)
                        print(f"成功插入圖片: {image_path}")
                    except Exception as e:
                        print(f"插入圖片失敗: {image_path}, 錯誤: {str(e)}")
                else:
                    print(f"未找到圖片文件: {image_filename} (在 {image_folder})")
                
                continue
                
            # 新的一頁（一級或二級標題）
            if line_stripped.startswith('# ') or line_stripped.startswith('## '):
                current_slide = prs.slides.add_slide(bullet_slide_layout)
                shapes = current_slide.shapes
                title_shape = shapes.title
                body_shape = shapes.placeholders[1]
                
                title_text = line.lstrip('#').strip()
                title_shape.text = title_text
                tf = body_shape.text_frame
                
            # 內容點
            elif current_slide and (line.startswith('- ') or line.startswith('* ')):
                if tf:
                    p = tf.add_paragraph()
                    p.text = line[2:]
                    p.level = 0
            
            # 普通文本作為內容
            elif current_slide and not line.startswith('#'):
                if tf:
                    p = tf.add_paragraph()
                    p.text = line
                    p.level = 0
                    
        return prs

    @staticmethod
    def markdown_to_pdf(content, doc_config, output_path):
        """將Markdown轉換為PDF"""
        
        # 註冊中文字體 (如果有的話，否則使用默認)
        # 這裡假設系統有微軟正黑體，如果沒有可能需要調整
        try:
            pdfmetrics.registerFont(TTFont('MsJhengHei', 'msjh.ttc'))
            font_name = 'MsJhengHei'
        except:
            try:
                pdfmetrics.registerFont(TTFont('ArialUnicode', 'arialuni.ttf'))
                font_name = 'ArialUnicode'
            except:
                font_name = 'Helvetica' #  fallback
        
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # 定義樣式
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontName=font_name,
            fontSize=24,
            spaceAfter=30
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading1'],
            fontName=font_name,
            fontSize=18,
            spaceBefore=20,
            spaceAfter=10
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=12,
            spaceBefore=6,
            leading=18
        )
        
        story = []
        
        # 添加標題
        story.append(Paragraph(doc_config.get('title', '生成的文檔'), title_style))
        story.append(Spacer(1, 12))
        
        # 處理內容
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                story.append(Spacer(1, 6))
                continue
                
            if line.startswith('# ') or line.startswith('## '):
                text = line.lstrip('#').strip()
                story.append(Paragraph(text, heading_style))
            elif line.startswith('- ') or line.startswith('* '):
                text = "• " + line[2:]
                story.append(Paragraph(text, normal_style))
            else:
                story.append(Paragraph(line, normal_style))
                
        doc.build(story)
        return output_path
