import json
import pandas as pd
import os
from app.core.processors.base_processor import BaseProcessor

class JsonProcessor(BaseProcessor):
    """處理JSON檔案並提取文本內容"""
    
    def process(self, file_path: str) -> str:
        """
        處理JSON檔案並提取文本
        
        Args:
            file_path: JSON檔案路徑
            
        Returns:
            提取的文本內容
        """
        if not self.validate(file_path):
            return "無效的檔案路徑"
        
        try:
            # 檢查檔案副檔名
            if file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 將JSON轉換為文本格式
                if isinstance(data, dict):
                    # 如果是字典，將鍵值對轉為文本
                    text_parts = []
                    for key, value in data.items():
                        text_parts.append(f"{key}: {value}")
                    return "\n".join(text_parts)
                elif isinstance(data, list):
                    # 如果是列表，嘗試提取所有文本字段
                    text_parts = []
                    for item in data:
                        if isinstance(item, dict):
                            item_parts = []
                            for key, value in item.items():
                                if isinstance(value, (str, int, float, bool)):
                                    item_parts.append(f"{key}: {value}")
                            text_parts.append("\n".join(item_parts))
                        else:
                            text_parts.append(str(item))
                    return "\n\n".join(text_parts)
                else:
                    # 其他情況轉為字符串
                    return str(data)
            
            # 處理Excel檔案 (參考提供的代碼)
            elif file_path.endswith(('.xlsx', '.xls')):
                output_text = ""
                filename = os.path.basename(file_path)
                
                # 處理 "基本問卷" 表單
                try:
                    df_basic = pd.read_excel(file_path, sheet_name="基本問卷")
                    if not df_basic.empty and "問題" in df_basic.columns and "答案" in df_basic.columns:
                        output_text += f"# 檔案: {filename} - 基本問卷\n\n"

                        for _, row in df_basic.iterrows():
                            question = row.get("問題", "")
                            answer = row.get("答案", "")
                            note = row.get("備註", "")

                            if pd.notna(question) and pd.notna(answer):
                                output_text += f"問題: {question}\n答案: {answer}\n"
                                if pd.notna(note):
                                    output_text += f"備註: {note}\n"
                                output_text += "\n"
                except Exception as e:
                    output_text += f"處理 '基本問卷' 表單時發生錯誤: {str(e)}\n\n"
                
                # 處理 "身型問卷" 表單
                try:
                    df_body = pd.read_excel(file_path, sheet_name="身型問卷")
                    if not df_body.empty and "問題" in df_body.columns and "答案" in df_body.columns:
                        output_text += f"# 檔案: {filename} - 身型問卷\n\n"

                        for _, row in df_body.iterrows():
                            question = row.get("問題", "")
                            answer = row.get("答案", "")
                            note = row.get("備註", "")

                            if pd.notna(question) and pd.notna(answer):
                                output_text += f"問題: {question}\n答案: {answer}\n"
                                if pd.notna(note):
                                    output_text += f"備註: {note}\n"
                                output_text += "\n"
                except Exception as e:
                    output_text += f"處理 '身型問卷' 表單時發生錯誤: {str(e)}\n\n"
                
                # 處理其他表單
                try:
                    excel_file = pd.ExcelFile(file_path)
                    for sheet_name in excel_file.sheet_names:
                        if sheet_name not in ["基本問卷", "身型問卷"]:
                            df = pd.read_excel(file_path, sheet_name=sheet_name)
                            if not df.empty:
                                output_text += f"# 檔案: {filename} - {sheet_name}\n\n"
                                output_text += df.to_string(index=False) + "\n\n"
                except Exception as e:
                    output_text += f"處理其他表單時發生錯誤: {str(e)}\n\n"
                
                return output_text
                
        except Exception as e:
            return f"處理檔案時發生錯誤: {str(e)}"
