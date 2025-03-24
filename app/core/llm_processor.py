import os
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from openai import OpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 加載環境變數
load_dotenv()

class LLMProcessor:
    """
    使用大型語言模型(LLM)處理文本的處理器
    """
    
    def __init__(self):
        """初始化LLM處理器"""
        # 確保必要的API金鑰設置
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.openai_client = self._initialize_openai_client() if self.openai_api_key else None
        
        # 報告儲存目錄
        self.reports_dir = "./reports"
        self._ensure_directory_exists(self.reports_dir)
        
        # 定義報告格式化的關鍵詞
        self.section_keywords = ["基本信息", "健康状况", "飲食習慣", "挑戰與目標", "總結", "結論", "建議"]

    def _initialize_openai_client(self) -> Optional[OpenAI]:
        """初始化OpenAI客戶端"""
        try:
            return OpenAI(api_key=self.openai_api_key)
        except Exception as e:
            logger.error(f"初始化OpenAI客戶端時出錯: {str(e)}")
            return None
            
    def _ensure_directory_exists(self, directory_path: str) -> bool:
        """確保指定的目錄存在，如果不存在則創建它"""
        try:
            Path(directory_path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"創建目錄 {directory_path} 時出錯: {str(e)}")
            return False
            
    def _save_report(self, report: str, identifier: str = "report") -> Optional[str]:
        """保存生成的報告到文件"""
        try:
            # 創建帶有時間戳的文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.reports_dir}/{identifier}_{timestamp}.md"
            
            # 保存報告
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
                
            logger.info(f"報告已儲存到 {filename}")
            return filename
        except Exception as e:
            logger.error(f"儲存報告時出錯: {str(e)}")
            return None
    
    def _process_with_openai(self, text_content: str, prompt: str, 
                            model: str = "gpt-4o-mini", retry_count: int = 3) -> str:
        """使用OpenAI模型處理文本，帶有重試邏輯"""
        if not self.openai_client:
            return "OpenAI客戶端未初始化，請檢查API金鑰"
            
        for attempt in range(retry_count):
            try:
                logger.info(f"使用OpenAI處理中 (嘗試 {attempt+1}/{retry_count})")
                response = self.openai_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a professional medical assistant."},
                        {"role": "user", "content": f"{prompt}\n\n{text_content}"}
                    ]
                )
                result = response.choices[0].message.content
                logger.info("OpenAI處理成功")
                return result
            except Exception as e:
                logger.error(f"OpenAI處理時出錯 (嘗試 {attempt+1}): {str(e)}")
                if attempt < retry_count - 1:
                    # 指數退避策略
                    wait_time = 2 ** attempt
                    logger.info(f"{wait_time} 秒後重試...")
                    time.sleep(wait_time)
                else:
                    return f"OpenAI處理時出錯 (嘗試 {retry_count} 次): {str(e)}"
    
    def _process_with_gemini(self, text_content: str, prompt: str, 
                            model: str = "gemini-2.0-flash", retry_count: int = 3) -> str:
        """使用Gemini模型處理文本，帶有重試邏輯"""
        if not self.google_api_key:
            return "Google API金鑰未設置，請檢查環境變數"
            
        for attempt in range(retry_count):
            try:
                logger.info(f"使用Gemini處理中 (嘗試 {attempt+1}/{retry_count})")
                llm = ChatGoogleGenerativeAI(model=model, google_api_key=self.google_api_key)
                result = llm.invoke(f"{prompt}\n\n{text_content}")
                logger.info("Gemini處理成功")
                return result.content
            except Exception as e:
                logger.error(f"Gemini處理時出錯 (嘗試 {attempt+1}): {str(e)}")
                if attempt < retry_count - 1:
                    # 指數退避策略
                    wait_time = 2 ** attempt
                    logger.info(f"{wait_time} 秒後重試...")
                    time.sleep(wait_time)
                else:
                    return f"Gemini處理時出錯 (嘗試 {retry_count} 次): {str(e)}"
    
    def _format_report(self, text: str) -> str:
        """將AI回應格式化為結構良好的營養報告，同時保留換行符"""
        # 添加具有獨特樣式的標題
        formatted_text = "# AI 醫生診前報告\n\n"
        
        # 逐行處理文本以維持結構並添加格式
        lines = text.split('\n')
        current_section = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                formatted_text += "\n"  # 保留空行以進行間隔
                continue
                
            # 檢查此行是否為小節標題
            is_section = False
            for keyword in self.section_keywords:
                if keyword in line and len(line) < 30:
                    # 這可能是一個小節標題
                    current_section = line
                    formatted_text += f"\n## {line}\n\n"
                    is_section = True
                    break
                    
            if not is_section:
                # 格式化鍵值對（帶有冒號的項目）
                if ":" in line or "：" in line:
                    parts = line.split(":", 1) if ":" in line else line.split("：", 1)
                    if len(parts) == 2 and len(parts[0]) < 20:  # 鍵值對
                        key = parts[0].strip()
                        value = parts[1].strip()
                        formatted_text += f"**{key}**：{value}\n\n"
                    else:
                        # 帶有冒號但不是鍵值對的常規行
                        formatted_text += f"{line}\n\n"
                else:
                    # 常規文本行
                    formatted_text += f"{line}\n\n"
                    
        return formatted_text
    
    def get_default_prompt(self) -> str:
        """獲取默認提示詞"""
        return """
**角色設定**
你是一位專業營養師，擅長將營養諮詢內容與問卷資料整理成醫生診療前的參考報告。
請根據客戶問卷資料和營養師與客戶對話語音諮詢的記錄，提煉關鍵資訊，撰寫一份簡潔易讀的報告，幫助醫生快速了解客戶的營養狀況與飲食需求。

**格式與內容**

簡短的重點摘要:確保醫生能迅速掌握核心資訊，使其能快速理解客戶的營養狀況與可能的介入方向。

詳細說明(＊＊以下問題必須都列出，如果沒找到資料給出空值＊＊):請以適合醫生閱讀的方式撰寫報告，以專業且清晰的語言呈現，但避免過於生硬或學術化。

1.客戶健康狀況
  預約看診動機：例如希望改善體重或健康或疾病狀況
  個人病史
  家族病史：無明確病史就講述疾病傾向例如家族成員易胖。
  肥胖史：曾經胖過的公斤數、胖起來的時間點、發胖原因？
  減重史：減重過程中遇到的挑戰與時機
  疾病史：疾病名稱、曾經的疾病相關檢測數據
  用藥史：列出現在使用中的明確藥名及用藥時間
  減重用藥：使用過減肥藥及保健品，現階段仍在使用的藥物。
  健檢數據：日期及檢測項目

2.生活型態
  * 睡眠狀態
  * 排便頻率
  * 工作史
  * 壓力
  * 每日餐食
    - 早餐
    - 午餐
    - 晚餐
* 非正餐飲食習慣
    - 點心
    - 零食
    - 飲料
  * 飲食習慣、飲食類型、飲食偏好、不吃的食物類別、水果甜點飲料食用頻率、飲水量及習慣
  * 客人特殊的事件

3.客人預期達到目標：
  最希望改善的部分、期待達成的目標

請先整合問卷資料與諮詢內容，再生成結構完整的報告。
最後確保報告完全正確且合理，不可額外添加資料中沒有的資訊。
請以最精簡的語言作答。
請無須做最後總結。
請以中英文兩個版本作答。
"""
    
    def process(self, text_content: str, prompt: Optional[str] = None, 
               model_choice: str = "OpenAI-4o-mini") -> Dict[str, Any]:
        """
        使用LLM處理文本並生成報告
        
        Args:
            text_content: 合併後的文本內容
            prompt: 可選的自定義提示詞
            model_choice: 選擇的模型 ("OpenAI-4o-mini" 或 "Gemini")
            
        Returns:
            包含處理結果的字典
        """
        try:
            logger.info(f"開始使用 {model_choice} 處理資料")
            
            # 使用默認提示詞（如果未提供）
            if not prompt:
                prompt = self.get_default_prompt()
                
            # 使用選定的AI模型進行處理
            if model_choice == "OpenAI-4o-mini":
                result = self._process_with_openai(text_content, prompt)
            else:  # Gemini
                result = self._process_with_gemini(text_content, prompt)
                
            # 格式化結果
            formatted_report = self._format_report(result)
            
            # 保存報告到文件
            report_path = self._save_report(formatted_report)
            
            logger.info("資料處理成功完成")
            
            return {
                "status": "success",
                "model_used": model_choice,
                "report": formatted_report,
                "report_path": report_path
            }
            
        except Exception as e:
            logger.error(f"處理資料時出錯: {str(e)}")
            error_message = f"處理資料時出錯: {str(e)}"
            
            return {
                "status": "error",
                "error": error_message
            }
            
    def batch_process(self, text_contents: List[str], prompt: Optional[str] = None, 
                     model_choice: str = "OpenAI-4o-mini") -> List[Dict[str, Any]]:
        """
        批量處理多個文本並生成多份報告
        
        Args:
            text_contents: 文本內容列表
            prompt: 可選的自定義提示詞
            model_choice: 選擇的模型
            
        Returns:
            包含處理結果的字典列表
        """
        results = []
        
        for i, content in enumerate(text_contents):
            logger.info(f"處理第 {i+1}/{len(text_contents)} 個文本")
            result = self.process(content, prompt, model_choice)
            result["index"] = i + 1
            results.append(result)
            
        return results
