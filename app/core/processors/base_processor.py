from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseProcessor(ABC):
    """
    處理器基礎類別，定義共用介面
    """
    
    @abstractmethod
    def process(self, file_path: str) -> str:
        """
        處理檔案並返回提取的文本
        
        Args:
            file_path: 檔案路徑
            
        Returns:
            提取的文本內容
        """
        pass
    
    def validate(self, file_path: str) -> bool:
        """
        驗證檔案是否可處理
        
        Args:
            file_path: 檔案路徑
            
        Returns:
            檔案是否有效
        """
        import os
        return os.path.exists(file_path)
    
    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        獲取檔案元數據
        
        Args:
            file_path: 檔案路徑
            
        Returns:
            檔案元數據
        """
        import os
        return {
            "file_name": os.path.basename(file_path),
            "file_size": os.path.getsize(file_path),
            "file_type": os.path.splitext(file_path)[1],
            "last_modified": os.path.getmtime(file_path)
        }
