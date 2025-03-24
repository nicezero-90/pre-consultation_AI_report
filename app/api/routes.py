from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional
import os
from app.core.processors.json_processor import JsonProcessor
from app.core.processors.mp4_processor import Mp4Processor
from app.core.processors.text_processor import TextProcessor
from app.core.llm_processor import LLMProcessor

router = APIRouter()

# 臨時存儲上傳文件的目錄
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/process")
async def process_files(
    files: List[UploadFile] = File(...),
    prompt: Optional[str] = Form(None)
):
    """
    接收並處理上傳的檔案，支援JSON、MP4和TXT格式
    """
    if not files:
        raise HTTPException(status_code=400, detail="沒有上傳檔案")
    
    # 存儲處理結果
    processed_texts = []
    
    # 處理每個檔案
    for file in files:
        # 保存上傳的檔案
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        # 根據檔案類型選擇處理器
        if file.filename.endswith(".json"):
            processor = JsonProcessor()
        elif file.filename.endswith(".mp4"):
            processor = Mp4Processor()
        elif file.filename.endswith(".txt"):
            processor = TextProcessor()
        else:
            # 刪除不支援的檔案
            os.remove(file_path)
            continue
        
        # 處理檔案並獲取文本
        text = processor.process(file_path)
        processed_texts.append(text)
        
        # 處理完畢後刪除檔案
        os.remove(file_path)
    
    # 如果沒有成功處理任何檔案
    if not processed_texts:
        raise HTTPException(status_code=400, detail="沒有有效的檔案可處理")
    
    # 合併所有處理後的文本
    combined_text = "\n\n".join(processed_texts)
    
    # 使用LLM處理器生成最終報告
    llm_processor = LLMProcessor()
    result = llm_processor.process(combined_text, prompt)
    
    return {"result": result}

@router.get("/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "healthy"}
