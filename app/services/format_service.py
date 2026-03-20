import os
import re
from docx import Document
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.xmlchemy import OxmlElement

def SubElement(parent, tagname, **kwargs):
    element = OxmlElement(tagname)
    element.attrib.update(kwargs)
    parent.append(element)
    return element

def _set_cell_border(cell, border_color="FFFFFF", border_width='12700'):
    """
    設定儲存格邊框
    border_width: 12700 = 1pt
    """
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    
    # 設定四邊邊框
    for border in ['lnL', 'lnR', 'lnT', 'lnB']:
        ln = SubElement(tcPr, 'a:' + border, w=border_width, cap='flat', cmpd='sng', algn='ctr')
        solidFill = SubElement(ln, 'a:solidFill')
        SubElement(solidFill, 'a:srgbClr', val=border_color)
        SubElement(ln, 'a:prstDash', val='solid')
        SubElement(ln, 'a:round')
        SubElement(ln, 'a:headEnd', type='none', w='med', len='med')
        SubElement(ln, 'a:tailEnd', type='none', w='med', len='med')




def parse_markdown_table(lines, start_index):
    """
    解析 Markdown 表格
    
    Args:
        lines: 所有文字行
        start_index: 表格開始的索引
        
    Returns:
        (headers, rows, end_index) 或 (None, None, start_index) 如果不是表格
    """
    if start_index >= len(lines):
        return None, None, start_index
    
    first_line = lines[start_index].strip()
    
    # 如果是列表項，去除前綴
    if first_line.startswith('- ') or first_line.startswith('* '):
        first_line = first_line[2:].strip()
    
    # 檢查是否為表格行（包含 |）
    if '|' not in first_line:
        return None, None, start_index
    
    # 解析表頭
    headers = [cell.strip() for cell in first_line.split('|') if cell.strip()]
    
    # 檢查下一行是否為分隔線（如 |---|---|）
    if start_index + 1 >= len(lines):
        return None, None, start_index
    
    separator_line = lines[start_index + 1].strip()
    if not re.match(r'^[\|\s:\-]+$', separator_line):
        return None, None, start_index
    
    # 解析資料行
    rows = []
    end_index = start_index + 2
    
    while end_index < len(lines):
        line = lines[end_index].strip()
        if '|' not in line or line == '' or line.startswith('#'):
            break
        cells = [cell.strip() for cell in line.split('|') if cell.strip()]
        if cells:
            rows.append(cells)
        end_index += 1
    
    return headers, rows, end_index


def create_pptx_table(slide, headers, rows, left=Inches(0.5), top=Inches(1.5), width=Inches(9.0),
                      header_font_size=Pt(11), content_font_size=Pt(10), column_widths=None):
    """
    在投影片中創建原生表格
    
    Args:
        slide: 投影片物件
        headers: 表頭列表
        rows: 資料行列表
        left: 左邊距
        top: 上邊距
        width: 表格寬度
        header_font_size: 表頭字體大小
        content_font_size: 內容字體大小
        column_widths: 欄位寬度比例列表（可選），例如 [0.1, 0.15, 0.6, 0.05, 0.05, 0.05] 總和應為 1.0
    
    Returns:
        table shape 物件
    """
    # 計算行數和列數
    num_rows = len(rows) + 1  # +1 for header
    num_cols = len(headers) if headers else (len(rows[0]) if rows else 1)
    
    # 計算表格高度（根據行數）
    row_height = Inches(0.4)
    height = row_height * num_rows
    
    # 創建表格
    table_shape = slide.shapes.add_table(num_rows, num_cols, left, top, width, height)
    table = table_shape.table
    
    # 設定每列寬度
    if column_widths and len(column_widths) == num_cols:
        # 使用自訂寬度比例
        for col in range(num_cols):
            table.columns[col].width = int(width * column_widths[col])
    else:
        # 平均分配寬度
        col_width = int(width / num_cols)
        for col in range(num_cols):
            table.columns[col].width = col_width
    
    # 設定表頭
    for col_idx, header_text in enumerate(headers):
        if col_idx < num_cols:
            cell = table.cell(0, col_idx)
            
            # 特殊處理表頭換行
            text = header_text
            if "主要工作內容" in text:
                text = text.replace("(", "\n(").replace("（", "\n（")
            elif "預計完成日" in text:
                text = text.replace("完成", "完成\n")
            
            cell.text = text
            # 設定表頭樣式（使用傳入的字體大小）
            paragraph = cell.text_frame.paragraphs[0]
            paragraph.font.bold = True
            paragraph.font.size = header_font_size
            paragraph.alignment = PP_ALIGN.CENTER
            # 設定表頭背景色（深藍色）
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(0, 51, 102)
            paragraph.font.color.rgb = RGBColor(255, 255, 255)
            
            # 設定表頭邊框（白色）
            _set_cell_border(cell, border_color="FFFFFF")
    
    # 設定資料行
    for row_idx, row_data in enumerate(rows):
        for col_idx, cell_text in enumerate(row_data):
            if col_idx < num_cols:
                cell = table.cell(row_idx + 1, col_idx)
                
                # 處理換行符號 <br>
                text_content = str(cell_text)
                # 將 <br>, <br/>, <BR> 等轉換為換行符號
                text_content = re.sub(r'<br\s*/?>', '\n', text_content, flags=re.IGNORECASE)
                
                cell.text = text_content
                
                # 設定資料行樣式（使用傳入的字體大小）
                # 遍歷所有段落設定字體，確保換行後字體一致
                for paragraph in cell.text_frame.paragraphs:
                    paragraph.font.size = content_font_size
                    paragraph.alignment = PP_ALIGN.LEFT
                
                # 交替背景色
                if row_idx % 2 == 0:
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = RGBColor(240, 240, 240)
                    
                # 設定資料格邊框（白色）
                _set_cell_border(cell, border_color="FFFFFF")
    
    return table_shape


class FormatConverter:
    """格式轉換器 - 將 Markdown 轉換為各種輸出格式"""

    @staticmethod
    def markdown_to_docx(content, doc_config, template_path=None):
        """將Markdown轉換為DOCX
        
        Args:
            content: Markdown 內容
            doc_config: 文檔配置
            template_path: 模板文件路徑（可選），如果是 DOCX 會繼承其樣式
        """
        # 如果模板是 DOCX，使用它作為基底（繼承樣式和背景）
        if template_path and template_path.lower().endswith('.docx'):
            try:
                doc = Document(template_path)
                # 移除模板原有內容，只保留樣式
                for element in list(doc.element.body):
                    doc.element.body.remove(element)
                print(f"[INFO] 使用 DOCX 模板作為基底: {template_path}")
            except Exception as e:
                print(f"[WARNING] 無法使用 DOCX 模板，使用空白文檔: {e}")
                doc = Document()
        else:
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
    def _convert_ppt_to_pptx(ppt_path):
        """
        使用 COM 將 .ppt 轉換為 .pptx (僅限 Windows)
        """
        import os
        try:
            import win32com.client
            import pythoncom
        except ImportError:
            print("[ERROR] 缺少 win32com 模組，無法轉換 .ppt 檔案")
            return None
            
        base, _ = os.path.splitext(ppt_path)
        pptx_path = base + "_converted.pptx"
        
        # 如果轉換後的文件存在且比源文件新，直接使用
        if os.path.exists(pptx_path):
            try:
                if os.path.getmtime(pptx_path) > os.path.getmtime(ppt_path):
                    print(f"[INFO] 使用已緩存的轉換檔案: {pptx_path}")
                    return pptx_path
            except Exception:
                pass # 如果比較時間失敗，就重新轉換
                
        powerpoint = None
        presentation = None
        try:
            pythoncom.CoInitialize()
            try:
                # 嘗試獲取現有的 PowerPoint 實例
                powerpoint = win32com.client.GetActiveObject("PowerPoint.Application")
            except Exception:
                # 如果沒有，創建新的
                powerpoint = win32com.client.Dispatch("PowerPoint.Application")
            
            abs_ppt_path = os.path.abspath(ppt_path)
            abs_pptx_path = os.path.abspath(pptx_path)
            
            print(f"[INFO] 正在轉換: {abs_ppt_path} -> {abs_pptx_path}")
            
            # WithWindow=False 避免彈出視窗
            presentation = powerpoint.Presentations.Open(abs_ppt_path, WithWindow=False)
            presentation.SaveAs(abs_pptx_path, 24) # 24 = ppSaveAsOpenXMLPresentation (*.pptx)
            
            return pptx_path
            
        except Exception as e:
            print(f"[ERROR] PPT 轉換失敗: {e}")
            return None
        finally:
            if presentation:
                try:
                    presentation.Close()
                except Exception:
                    pass
            # 不關閉 PowerPoint，避免影響使用者可能正在使用的視窗，或者保持進程以重用
    
    @staticmethod
    def markdown_to_pptx(content, doc_config, image_folder=None, template_path=None):
        """
        將Markdown轉換為PPTX
        
        Args:
            content: Markdown 內容
            doc_config: 文檔配置
            image_folder: 圖片文件夾路徑（可選）
            template_path: 模板文件路徑（可選），如果是 PPTX 會繼承其母片樣式
        """
        # 預設字體大小
        title_font_size = Pt(28)
        content_font_size = Pt(14)

        if template_path:
            # [Fix] 支援舊版 .ppt 格式：自動轉換為 .pptx
            if template_path.lower().endswith('.ppt'):
                print(f"[INFO] 檢測到 .ppt 格式，嘗試轉換為 .pptx: {template_path}")
                converted_path = FormatConverter._convert_ppt_to_pptx(template_path)
                if converted_path:
                    template_path = converted_path
                else:
                    print(f"[WARNING] .ppt 轉換失敗，將無法讀取模板內容")
        
        if template_path and template_path.lower().endswith('.pptx'):
            try:
                prs = Presentation(template_path)
                
                # 嘗試從模板的第一張投影片提取字體大小
                if len(prs.slides) > 0:
                    first_slide = prs.slides[0]
                    for shape in first_slide.shapes:
                        if shape.has_text_frame:
                            for para in shape.text_frame.paragraphs:
                                if para.font.size:
                                    font_size = para.font.size
                                    # 判斷是標題還是內容（根據字體大小判斷）
                                    if font_size >= Pt(20):
                                        title_font_size = font_size
                                        print(f"[INFO] 從模板提取標題字體大小: {font_size.pt}pt")
                                    elif font_size >= Pt(10):
                                        content_font_size = font_size
                                        print(f"[INFO] 從模板提取內容字體大小: {font_size.pt}pt")
                                    break
                
                # [Fix] 不要刪除所有投影片，保留第一張作為 Title Slide
                # 這樣可以保留 User 在第一張投影片上直接貼的圖（非 Master 樣式）
                
                # 嘗試刪除第一張之後的所有投影片
                try:
                    while len(prs.slides) > 1:
                        rId = prs.slides._sldIdLst[1].rId
                        prs.part.drop_rel(rId)
                        del prs.slides._sldIdLst[1]
                except Exception as del_err:
                    print(f"[WARNING] 刪除多餘投影片時發生錯誤 (但不影響使用模板): {del_err}")
                
                print(f"[INFO] 使用 PPTX 模板作為基底: {template_path}")
                if len(prs.slides) > 0:
                    print(f"[INFO] 保留原有第一張投影片作為標題頁 (保留背景圖)")
                
            except Exception as e:
                print(f"[WARNING] 無法使用 PPTX 模板，使用空白簡報: {e}")
                prs = Presentation()
        else:
            prs = Presentation()
        
        # 智能選擇版面配置
        # 需要根據名稱判斷哪個是真正的內容版面
        title_slide_layout = None
        bullet_slide_layout = None
        blank_slide_layout = None
        
        # 先列出所有版面以便除錯
        print(f"[DEBUG] 模板共有 {len(prs.slide_layouts)} 個版面:")
        for i, layout in enumerate(prs.slide_layouts):
            print(f"  [{i}] {layout.name}")
        
        # 遍歷版面，智能選擇
        for i, layout in enumerate(prs.slide_layouts):
            layout_name = layout.name.lower() if layout.name else ""
            layout_name_orig = layout.name if layout.name else ""
            
            # 標題版面（封面）：通常索引0，且名稱只有「標題」沒有「物件」或「內容」
            if title_slide_layout is None:
                if i == 0:  # 第一個通常是封面
                    title_slide_layout = layout
                elif "title" in layout_name and "content" not in layout_name and "物件" not in layout_name_orig:
                    title_slide_layout = layout
            
            # 內容版面：名稱包含「物件」、「內容」、「content」、「body」
            if bullet_slide_layout is None:
                if "物件" in layout_name_orig or "內容" in layout_name_orig:
                    bullet_slide_layout = layout
                    print(f"[DEBUG] 找到內容版面 (中文): [{i}] {layout.name}")
                elif "content" in layout_name or "body" in layout_name:
                    bullet_slide_layout = layout
                    print(f"[DEBUG] 找到內容版面 (英文): [{i}] {layout.name}")
            
            # 空白版面
            if blank_slide_layout is None:
                if "blank" in layout_name or "空白" in layout_name_orig:
                    blank_slide_layout = layout
        
        # 如果找不到「內容版面」，嘗試使用索引 1 或 2
        if bullet_slide_layout is None:
            if len(prs.slide_layouts) > 2:
                bullet_slide_layout = prs.slide_layouts[2]  # 很多模板第三個是內容版面
            elif len(prs.slide_layouts) > 1:
                bullet_slide_layout = prs.slide_layouts[1]
            elif len(prs.slide_layouts) > 0:
                bullet_slide_layout = prs.slide_layouts[0]
        
        # 如果找不到標題版面
        if title_slide_layout is None and len(prs.slide_layouts) > 0:
            title_slide_layout = prs.slide_layouts[0]
        
        if blank_slide_layout is None:
            blank_slide_layout = prs.slide_layouts[0]
        
        # 如果完全沒有版面，使用空白簡報
        if title_slide_layout is None:
            print("[WARNING] 模板沒有任何版面配置，使用空白簡報")
            prs = Presentation()
            title_slide_layout = prs.slide_layouts[0]
            bullet_slide_layout = prs.slide_layouts[1]
            blank_slide_layout = prs.slide_layouts[6]
        
        # 重要：如果「標題及物件」版面沒有內容區域，使用空白版面代替
        # 這樣我們可以完全控制 TextBox 的位置
        # [Fix] 使用者反映背景圖片消失，因為這裡強制切換到空白版面（通常沒有背景設計）
        # 因後續代碼是直接創建 TextBox，使用原始的內容版面（帶背景）也不會影響文字排版
        # if bullet_slide_layout and blank_slide_layout:
        #     print(f"[INFO] 內容頁將使用空白版面 '{blank_slide_layout.name}'，並自動創建 TextBox")
        #     bullet_slide_layout = blank_slide_layout  # 使用空白版面作為內容版面
        
        print(f"[INFO] 標題版面: {title_slide_layout.name}, 內容版面: {bullet_slide_layout.name if bullet_slide_layout else 'None'}")
        
        # 創建標題頁 (如果是新簡報或模板已被清空)
        slide = None
        if len(prs.slides) > 0:
            slide = prs.slides[0]
            # 清空原有標題文字（如果有）- 不清空 Shape，只清空 Text，避免刪到背景圖
            # 但我們直接覆蓋 slide.shapes.title.text 即可
        else:
            slide = prs.slides.add_slide(title_slide_layout)
        
        # 設定標題（如果有的話）
        if slide.shapes.title:
            slide.shapes.title.text = doc_config.get('title', '生成的演示文稿')
        
        # 設定副標題（如果有的話）
        try:
            if 1 in [p.placeholder_format.idx for p in slide.placeholders]:
                slide.placeholders[1].text = "由 AI 自動生成"
        except Exception:
            pass  # 沒有副標題 placeholder 就跳過
        
        current_slide = None
        body_shape = None
        tf = None
        
        # 圖片標記的正則表達式：支持多種格式
        # 格式1: [圖片 1-1: 來自投影片 1]
        # 格式2: - 圖片 1-1: 來自投影片 1
        image_pattern = re.compile(r'[-\[]?\s*圖片\s+(\d+)-(\d+)(?::\s*來自投影片\s*\d+)?[\]]?')
        
        lines = content.split('\n')
        line_index = 0
        
        while line_index < len(lines):
            line = lines[line_index]
            line_stripped = line.strip()
            
            if not line_stripped:
                line_index += 1
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
                
                if image_path:
                    # 如果當前沒有投影片，創建一個帶標題的投影片
                    if not current_slide:
                        current_slide = prs.slides.add_slide(bullet_slide_layout)
                        shapes = current_slide.shapes
                        if shapes.title:
                            shapes.title.text = "圖片內容"
                        # 安全取得 body_shape
                        body_shape = None
                        try:
                            if 1 in [p.placeholder_format.idx for p in current_slide.placeholders]:
                                body_shape = current_slide.placeholders[1]
                                tf = body_shape.text_frame
                        except Exception:
                            tf = None
                    
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
                
                line_index += 1
                continue
                
            # 新的一頁（一級或二級標題）
            if line_stripped.startswith('# ') or line_stripped.startswith('## '):
                current_slide = prs.slides.add_slide(bullet_slide_layout)
                shapes = current_slide.shapes
                
                # 取得標題文字
                title_text = line.lstrip('#').strip()
                
                # 檢查版面是否有標題 placeholder
                if shapes.title:
                    shapes.title.text = title_text
                    # [Fix] 即使是 Placeholder 也強制設定字體大小為 32 並上移
                    try:
                        # 強制設定位置和大小，避免因為寬度太窄導致文字變成直式排列(換行)
                        shapes.title.top = Inches(0.2)
                        shapes.title.left = Inches(0.5)
                        shapes.title.width = Inches(9.0)
                        shapes.title.height = Inches(1.0)
                        
                        shapes.title.text_frame.word_wrap = True
                        
                        for paragraph in shapes.title.text_frame.paragraphs:
                            paragraph.font.size = Pt(32)
                            paragraph.font.bold = True
                    except Exception as e:
                        print(f"[WARNING] 無法調整標題樣式: {e}")
                    print(f"[DEBUG] 使用 placeholder 設定標題 (強制 32pt, Top 0.2, Wide)")
                else:
                    # 空白版面沒有標題 placeholder，創建標題 TextBox
                    print(f"[DEBUG] 空白版面，創建標題 TextBox")
                    # [Fix] 上移標題位置 (0.3 -> 0.2)，調整字體大小為 32
                    title_box = shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(9), Inches(1.0))
                    title_box.text_frame.paragraphs[0].text = title_text
                    # 設定標題樣式
                    title_box.text_frame.paragraphs[0].font.size = Pt(32)
                    title_box.text_frame.paragraphs[0].font.bold = True
                
                # 除錯：列出所有 placeholders
                print(f"[DEBUG] Slide placeholders: {len(list(current_slide.placeholders))} 個")
                
                # 對於空白版面，直接創建內容 TextBox
                print(f"[INFO] 創建內容 TextBox")
                # 在標題下方創建一個 TextBox
                left = Inches(0.5)
                top = Inches(1.5)  # 標題下方
                width = Inches(9)
                height = Inches(5.5)
                textbox = shapes.add_textbox(left, top, width, height)
                tf = textbox.text_frame
                tf.word_wrap = True
                
                line_index += 1
                continue
            
            # 檢查是否為 Markdown 表格
            # 放寬條件：即使是列表項（- 開頭），只要包含 | 且能被解析為表格，就視為表格
            if current_slide and '|' in line_stripped:
                headers, rows, new_index = parse_markdown_table(lines, line_index)
                if headers:  # 只要有表頭就視為表格
                    # 如果沒有資料行，自動補三行空資料，以顯示空表格
                    if not rows:
                        rows = [['' for _ in headers] for _ in range(3)]
                        print(f"[INFO] 表格無資料，自動補入三行空資料")
                        
                    print(f"[INFO] 發現表格：{len(headers)} 列 x {len(rows)} 行")
                    
                    # 檢查是否為工作報告表格（包含「主要工作內容」欄位）
                    column_widths = None
                    is_work_report = False
                    if any('主要工作內容' in str(h) for h in headers):
                        is_work_report = True
                        # 工作報告表格：6個欄位 (項次, 專案名稱, 主要工作內容, 進度%, 預計完成日, 需求人)
                        # 自訂寬度比例：項次 6%, 專案名稱 12%, 主要工作內容 55%, 進度% 6%, 預計完成日 12%, 需求人 8%
                        column_widths = [0.06, 0.12, 0.55, 0.06, 0.12, 0.09]  # 總和 1.00
                        print(f"[INFO] 檢測到工作報告表格，使用自訂欄位寬度: {column_widths}")
                    
                    # 工作報告表格自動分頁邏輯
                    if is_work_report and len(rows) > 0:
                        MAX_ROWS_PER_PAGE = 8  # 每頁最多顯示 8 個專案（工作內容多時列高較高，超過即分頁）
                        
                        # 計算需要的頁數
                        total_pages = (len(rows) + MAX_ROWS_PER_PAGE - 1) // MAX_ROWS_PER_PAGE
                        
                        if total_pages > 1:
                            print(f"[INFO] 工作報告表格包含 {len(rows)} 行，將分為 {total_pages} 頁")
                        
                        # 保存原始標題
                        original_title = current_slide.shapes.title.text if current_slide.shapes.title else "本月工作報告"
                        
                        # 分頁處理
                        for page_num in range(total_pages):
                            start_idx = page_num * MAX_ROWS_PER_PAGE
                            end_idx = min(start_idx + MAX_ROWS_PER_PAGE, len(rows))
                            page_rows = rows[start_idx:end_idx]
                            
                            # 如果是第一頁，使用當前投影片；否則創建新投影片
                            if page_num == 0:
                                shapes = current_slide.shapes
                                # 有多頁時，第一頁標題也加 (1/N)
                                if total_pages > 1:
                                    title_text = f"{original_title} (1/{total_pages})"
                                    if shapes.title:
                                        shapes.title.text = title_text
                                        try:
                                            shapes.title.top = Inches(0.2)
                                            shapes.title.left = Inches(0.5)
                                            shapes.title.width = Inches(9.0)
                                            shapes.title.height = Inches(1.0)
                                            shapes.title.text_frame.word_wrap = True
                                            for paragraph in shapes.title.text_frame.paragraphs:
                                                paragraph.font.size = Pt(32)
                                                paragraph.font.bold = True
                                        except Exception as e:
                                            print(f"[WARNING] 無法調整標題樣式: {e}")
                                        print(f"[DEBUG] 第 1 頁標題更新為: {title_text}")
                            else:
                                current_slide = prs.slides.add_slide(bullet_slide_layout)
                                shapes = current_slide.shapes
                                
                                # 設定標題 (加上頁碼)
                                title_text = f"{original_title} ({page_num + 1}/{total_pages})"
                                
                                if shapes.title:
                                    shapes.title.text = title_text
                                    # 套用標題樣式
                                    try:
                                        shapes.title.top = Inches(0.2)
                                        shapes.title.left = Inches(0.5)
                                        shapes.title.width = Inches(9.0)
                                        shapes.title.height = Inches(1.0)
                                        shapes.title.text_frame.word_wrap = True
                                        for paragraph in shapes.title.text_frame.paragraphs:
                                            paragraph.font.size = Pt(32)
                                            paragraph.font.bold = True
                                    except Exception as e:
                                        print(f"[WARNING] 無法調整標題樣式: {e}")
                                    print(f"[DEBUG] 創建第 {page_num + 1} 頁，標題: {title_text}")
                            
                            # 在投影片中創建表格
                            create_pptx_table(current_slide, headers, page_rows,
                                              left=Inches(0.5), top=Inches(1.5), width=Inches(9.0),
                                              header_font_size=content_font_size, 
                                              content_font_size=content_font_size,
                                              column_widths=column_widths)
                        
                        # 跳過已處理的表格行
                        line_index = new_index
                        tf = None
                        continue
                    else:
                        # 非工作報告表格或資料行數不超過限制，使用原有邏輯
                        # 在當前投影片中創建原生表格（使用模板字體大小）
                        create_pptx_table(current_slide, headers, rows, 
                                          left=Inches(0.5), top=Inches(1.5), width=Inches(9.0),
                                          header_font_size=content_font_size, content_font_size=content_font_size,
                                          column_widths=column_widths)
                        # 跳過已處理的表格行
                        line_index = new_index
                        tf = None  # 表格後不再使用原有的 TextFrame
                        continue
                
            # 內容點
            if current_slide and (line.startswith('- ') or line.startswith('* ')):
                if tf:
                    p = tf.add_paragraph()
                    p.text = line[2:]
                    p.level = 0
                    p.font.size = content_font_size
            
            # 普通文本作為內容
            elif current_slide and not line.startswith('#'):
                if tf:
                    p = tf.add_paragraph()
                    p.text = line
                    p.level = 0
                    p.font.size = content_font_size
            
            line_index += 1
                    
        return prs

    @staticmethod
    def markdown_to_pdf(content, doc_config, output_path):
        """將Markdown轉換為PDF"""
        
        # 導入 reportlab (延遲導入，避免未安裝時影響其他功能)
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
        except ImportError:
            raise ImportError("PDF 生成功能需要安裝 reportlab。請執行: pip install reportlab")
        
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
