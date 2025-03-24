from app.core.processors.base_processor import BaseProcessor
import os

class TextProcessor(BaseProcessor):
    """處理文本檔案"""
    
    def process(self, file_path: str) -> str:
        """
        處理文本檔案並返回內容
        
        Args:
            file_path: 文本檔案路徑
            
        Returns:
            檔案內容
        """
        if not self.validate(file_path):
            return "無效的檔案路徑"
        
        try:
            # 嘗試不同的編碼讀取文件
            encodings = ['utf-8', 'cp950', 'big5', 'gbk']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    
                    # 添加檔案名稱作為標題
                    filename = os.path.basename(file_path)
                    formatted_content = f"# 檔案: {filename}\n\n{content}\n\n"
                    return formatted_content
                except UnicodeDecodeError:
                    continue
            
            # 如果所有編碼都失敗，嘗試以二進制方式讀取
            with open(file_path, 'rb') as f:
                binary_content = f.read()
                
                # 嘗試檢測編碼
                try:
                    import chardet
                    detected = chardet.detect(binary_content)
                    encoding = detected['encoding']
                    
                    if encoding:
                        content = binary_content.decode(encoding)
                        filename = os.path.basename(file_path)
                        formatted_content = f"# 檔案: {filename}\n\n{content}\n\n"
                        return formatted_content
                except (ImportError, Exception) as e:
                    pass
            
            return f"無法讀取檔案: {os.path.basename(file_path)}，請檢查檔案編碼"
            
        except Exception as e:
            return f"處理文本檔案時發生錯誤: {str(e)}"
