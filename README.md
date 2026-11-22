# 掌上中大 | NCU Campus Guide

中央大學校園資訊整合平台（課程專題開發中）。

## 專題簡介

希望將校園建築物、行政處室、常用業務與官方資訊連結整合至同一個介面，協助學生快速找到需要的資訊。

## 主要功能（目前起始版本）

- 顯示可縮放的 OpenStreetMap 校園地圖。
- 讀取 `data/locations.json`，標記已提供座標的建築物。
- 依建築名稱、簡介、處室、業務及關鍵字搜尋。
- 展開搜尋結果，查看行政業務及官方連結。

**現階段尚未匯入正式校園資料，也尚未加入 AI 語意搜尋。** 系統以功能骨架為主，請勿將其描述為完整可用的校園資料服務。

## 技術

- Python
- Streamlit（網站介面）
- Folium 與 streamlit-folium（互動地圖）
- JSON（靜態校園資料）

## 安裝與執行

先安裝 Python 3.10 以上版本，再於終端機執行：

```bash
git clone https://github.com/ping1shinichi-maker/ncu-campus-guide.git
cd ncu-campus-guide
python -m venv .venv
```

macOS / Linux：

```bash
source .venv/bin/activate
```

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
```

接著安裝依賴並啟動：

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Streamlit 通常會在瀏覽器開啟本機網站，預設網址為 `http://localhost:8501`。

## 操作流程

1. 啟動網站，查看校園附近的地圖。
2. 在 `data/locations.json` 加入已核對的建築物、處室與業務資料。
3. 重新整理後，透過搜尋欄查詢關鍵字。
4. 點選地圖標記或展開右側搜尋結果，查看相關資訊。

## 資料格式

`data/locations.json` 最外層是一個陣列，每筆建築資料可使用下列格式（**以下僅示意結構，非真實校園資料**）：

```json
[
  {
    "name": "示例建築",
    "latitude": 24.0,
    "longitude": 121.0,
    "description": "示例說明",
    "units": [
      {
        "name": "示例處室",
        "services": [
          {
            "name": "示例業務",
            "keywords": ["示例關鍵字"],
            "url": "https://example.org"
          }
        ]
      }
    ]
  }
]
```

請勿將示例座標或網址當作正式資料。每筆實際校園資訊應附上可信的官方來源，並定期檢查有效性。

## 後續規劃

- 蒐集、核對校園建築及行政服務資料。
- 完成搜尋結果與地圖定位連動。
- 視時程加入 AI 語意搜尋與測試。
- 優化手機介面、部署公開 Demo 網站。

## GitHub 團隊協作

請每位組員使用自己的 GitHub 帳號提交程式，使用清楚的 Commit 訊息（例如 `feat: add campus data`、`fix: correct map marker`），以便展示各自貢獻和版本演進。重要修改可使用獨立 branch 與 Pull Request。

請勿提交 API Key、密碼、個人資料或 `.streamlit/secrets.toml` 等機敏檔案。

## 資料標示

地圖底圖來源：© OpenStreetMap contributors。校園行政業務以中央大學最新官方公告為準。
