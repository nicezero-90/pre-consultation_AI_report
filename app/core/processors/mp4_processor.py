import os
import tempfile
import moviepy.editor as mp
from app.core.processors.base_processor import BaseProcessor
from app.config import settings

class Mp4Processor(BaseProcessor):
    """處理MP4影片檔案並使用Whisper生成文本"""
    
    def process(self, file_path: str) -> str:
        """
        處理MP4影片檔案並使用Whisper提取語音文本
        
        Args:
            file_path: MP4檔案路徑
            
        Returns:
            提取的語音文本
        """
        if not self.validate(file_path):
            return "無效的檔案路徑"
        
        try:
            # 創建臨時目錄來存儲MP3文件
            with tempfile.TemporaryDirectory() as temp_dir:
                # 將MP4轉換為MP3
                mp3_path = os.path.join(temp_dir, os.path.splitext(os.path.basename(file_path))[0] + ".mp3")
                
                try:
                    # 使用moviepy轉換MP4到MP3
                    video = mp.VideoFileClip(file_path)
                    audio = video.audio
                    audio.write_audiofile(mp3_path, verbose=False, logger=None)
                    video.close()
                    audio.close()
                except Exception as e:
                    return f"轉換MP4到MP3時發生錯誤: {str(e)}"
                
                # 使用OpenAI Whisper API進行轉錄
                try:
                    # 檢查是否安裝OpenAI庫
                    try:
                        from openai import OpenAI
                    except ImportError:
                        return "請安裝OpenAI庫: pip install openai"
                    
                    # 檢查API密鑰是否有效
                    api_key = settings.OPENAI_API_KEY
                    if not api_key:
                        return "OpenAI API密鑰未設置，請在.env檔案中設置OPENAI_API_KEY"
                    
                    # 初始化OpenAI客戶端
                    client = OpenAI(api_key=api_key)
                    
                    # 嘗試繁簡轉換
                    try:
                        import opencc
                        converter = opencc.OpenCC('s2twp')  # s2twp converts Simplified to Traditional Chinese (Taiwan)
                    except ImportError:
                        converter = None
                    
                    # 開啟音頻檔案
                    with open(mp3_path, "rb") as audio_file:
                        # 調用Whisper API
                        transcript = client.audio.transcriptions.create(
                            model="whisper-1",
                            file=audio_file,
                            language="zh"  # 中文語言
                        )
                    
                    # 轉為繁體中文(如果有安裝opencc)
                    text = transcript.text
                    if converter:
                        text = converter.convert(text)
                    
                    # 添加檔案信息和轉錄文本
                    output_text = f"# 檔案: {os.path.basename(file_path)}\n\n{text}\n\n"
                    return output_text
                    
                except Exception as e:
                    return f"使用Whisper API轉錄時發生錯誤: {str(e)}"
                
        except Exception as e:
            return f"處理MP4檔案時發生錯誤: {str(e)}"
