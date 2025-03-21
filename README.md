一個使用FastAPI建構的多媒體處理應用，可同時處理JSON、TXT和MP4文件，並使用OpenAI API生成整合報告。

## 系統架構圖

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                FastAPI 應用                              │
└───────────┬─────────────┬────────────────┬────────────────┬─────────────┘
            │             │                │                │
            ▼             ▼                ▼                ▼
┌───────────────┐  ┌─────────────┐  ┌────────────┐  ┌────────────────────┐
│  檔案上傳處理   │  │ JSON處理模組  │  │ TXT處理模組 │  │   MP4處理模組       │
└───────┬───────┘  └──────┬──────┘  └──────┬─────┘  └──────────┬─────────┘
        │                 │                │                   │
        │                 ▼                │                   ▼
        │          ┌─────────────┐         │           ┌────────────────┐
        │          │ 提取文字內容  │         │           │ OpenAI Whisper │
        │          └──────┬──────┘         │           └──────────┬─────┘
        │                 │                │                      │
        │                 ▼                ▼                      ▼
        │                 └───────────────────────────────────────┐
        │                                                         │
        ▼                                                         ▼
┌──────────────────┐                                      ┌─────────────────┐
│     安全模組      │                                      │   3個TXT內容     │
│ (.env檔案管理)    │                                      └────────┬────────┘
└─────────┬────────┘                                               │
          │                                                        ▼
          │                                                ┌─────────────────┐
          └───────────────────────────────────────────────►  OpenAI LLM API  │
                                                           └────────┬────────┘
                                                                    │
                                                                    ▼
                                                           ┌─────────────────┐
                                                           │  整合TXT報告     │
                                                           └────────┬────────┘
                                                                    │
                                                                    ▼
                                                           ┌─────────────────┐
                                                           │  FastAPI 回傳    │
                                                           └─────────────────┘
```

## 功能說明

此專案實現以下功能：

1. **多媒體檔案處理**：
   - 同時接收並處理JSON、TXT和MP4文件
   - 從JSON中提取文字內容
   - 處理純文字TXT檔案
   - 使用OpenAI Whisper將MP4轉換為文字

2. **OpenAI整合**：
   - 使用OpenAI API將三個文字來源整合為單一報告
   - 保護API金鑰不上傳至GitHub

3. **FastAPI介面**：
   - 提供簡單的RESTful API介面
   - 處理檔案上傳和結果回傳

## 專案結構

```
project-root/
│
├── .gitignore                # 包含.env和其他不該進入git的文件
├── .env.example              # 展示需要的環境變數，但不包含實際值
├── requirements.txt          # 專案依賴
├── README.md                 # 專案說明文檔
│
├── app/                      # 主要應用程式目錄
│   ├── __init__.py
│   ├── main.py               # FastAPI主入口點
│   ├── config.py             # 載入環境變數的設定
│   │
│   ├── api/                  # API相關模組
│   │   ├── __init__.py
│   │   ├── routes.py         # FastAPI路由定義
│   │
│   ├── core/                 # 核心功能模組
│   │   ├── __init__.py
│   │   ├── json_processor.py # 處理JSON並提取txt
│   │   ├── mp4_processor.py  # 處理MP4檔案並使用Whisper生成txt
│   │   ├── text_processor.py # 處理txt檔案
│   │   ├── llm_processor.py  # 使用OpenAI API整合txt報告
│
└── tests/                    # 測試目錄
    ├── __init__.py
    ├── test_json_processor.py
    ├── test_mp4_processor.py
    ├── test_text_processor.py
    ├── test_llm_processor.py
    │
    ├── data/                 # 測試資料目錄
    │   ├── input/            # 測試輸入檔案目錄
    │   └── output/           # 測試輸出檔案目錄
```

## 在Google Colab上使用

### 設置步驟

1. **複製GitHub專案到Colab**：
   ```python
   !git clone https://github.com/your-username/your-repo-name.git
   %cd your-repo-name
   ```

2. **建立環境變數檔案**：
   ```python
   %%writefile .env
   OPENAI_API_KEY=your_openai_api_key_here
   DEBUG=False
   ```

3. **安裝相依套件**：
   ```python
   !pip install -r requirements.txt
   ```

4. **啟動FastAPI伺服器**：
   ```python
   !uvicorn app.main:app --reload --host=0.0.0.0 --port=8000
   ```

5. **取得公開URL** (使用ngrok或Colab提供的URL轉發)：
   ```python
   from google.colab import output
   output.serve_kernel_port_as_window(8000)
   ```

### 使用API

API端點：`POST /process-files/`

請求格式：
- `multipart/form-data`
- 欄位：
  - `json_file`: JSON檔案
  - `txt_file`: TXT檔案
  - `mp4_file`: MP4檔案

回應格式：
- `application/json`
- 包含生成的整合報告URL

## 部署到GitHub

1. **移除或保護敏感資訊**：
   ```python
   !git rm --cached .env
   !echo ".env" >> .gitignore
   ```

2. **提交變更**：
   ```python
   !git add .
   !git commit -m "Initial commit"
   ```

3. **推送到GitHub**：
   ```python
   !git push origin main
   ```

## 依賴套件

- fastapi
- uvicorn
- python-multipart
- python-dotenv
- openai
- ffmpeg-python
- pydantic

## 注意事項

- 請確保您的OpenAI API金鑰有足夠的額度
- MP4處理需要安裝ffmpeg
- 上傳檔案大小可能受到限制
