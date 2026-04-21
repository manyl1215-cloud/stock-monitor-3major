# 📊 三大法人買賣監測系統 (Python 版本)

Taiwan Stock Institutional Investors Monitor - Python Edition

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Actions](https://github.com/your-username/stock-monitor/workflows/三大法人監測系統/badge.svg)](https://github.com/your-username/stock-monitor/actions)

## 🌟 功能特色

- ✅ **自動抓取資料**：每天從台灣證券交易所抓取三大法人（外資、投信、自營商）買賣數據
- 📊 **智慧分析**：
  - 大額交易警示（可自訂門檻）
  - 連續買賣趨勢追蹤
  - 個股籌碼集中分析
- 📧 **精美 Email 報告**：每日自動寄送 HTML 格式的分析報告
- 💾 **歷史資料儲存**：JSON 格式儲存，可回溯分析
- 🤖 **GitHub Actions 自動執行**：完全免費，無需伺服器
- 🐍 **純 Python 實作**：易於客製化和擴展

---

## 📦 快速開始

### 方法 1：GitHub Actions 自動執行（推薦 - 完全免費！）

1. **Fork 此專案**
   - 點選右上角的「Fork」按鈕

2. **設定 Secrets**
   - 進入你的 Repository
   - Settings > Secrets and variables > Actions
   - 點選「New repository secret」，新增以下 Secrets：
   
   | Name | Value | 說明 |
   |------|-------|------|
   | `EMAIL_TO` | `manyl1215@gmail.com` | 收件人 Email |
   | `SMTP_USER` | `your-email@gmail.com` | Gmail 帳號 |
   | `SMTP_PASSWORD` | `your-app-password` | Gmail 應用程式密碼 |
   | `WATCH_LIST` | `2330,2317,2454` | 監測股票（可選） |

3. **啟用 GitHub Actions**
   - Actions > 點選「I understand my workflows, go ahead and enable them」

4. **測試執行**
   - Actions > 三大法人監測系統 > Run workflow

5. **完成！**
   - 系統會在每天晚上 6 點自動執行
   - 你會收到分析報告的 Email

---

### 方法 2：本地執行

#### 1. Clone 專案
```bash
git clone https://github.com/your-username/stock-monitor.git
cd stock-monitor
```

#### 2. 安裝相依套件
```bash
pip install -r requirements.txt
```

#### 3. 設定環境變數
```bash
# 複製環境變數範例檔
cp .env.example .env

# 編輯 .env 檔案，填入你的設定
nano .env  # 或使用其他編輯器
```

#### 4. 執行程式
```bash
# 單次執行
python main.py

# 或使用排程執行（每天晚上 6 點）
python scheduler.py
```

---

## ⚙️ 設定說明

### Gmail 應用程式密碼設定

1. 前往 [Google 帳戶](https://myaccount.google.com/)
2. 左側選單：安全性
3. 「登入 Google」區塊：兩步驟驗證（必須先啟用）
4. 頁面底部：應用程式密碼
5. 選擇「郵件」和「其他」，輸入「股市監測」
6. 複製產生的 16 碼密碼
7. 將密碼填入 `.env` 的 `SMTP_PASSWORD`

### 監測股票清單

在 `.env` 中設定 `WATCH_LIST`：

```bash
# 監測特定股票
WATCH_LIST=2330,2317,2454,2882,2412

# 監測所有股票（留空）
WATCH_LIST=
```

### 調整警示門檻

```bash
# 大盤大額買賣門檻（億元）
THRESHOLD_MARKET_LARGE=50

# 個股大額買賣門檻（億元）
THRESHOLD_STOCK_LARGE=0.5

# 連續買賣天數門檻
THRESHOLD_CONSECUTIVE_DAYS=3
```

---

## 📂 專案結構

```
stock-monitor/
├── main.py                 # 主程式
├── modules/                # 模組套件
│   ├── __init__.py
│   ├── fetcher.py         # 資料抓取模組
│   ├── analyzer.py        # 資料分析模組
│   ├── emailer.py         # Email 發送模組
│   └── storage.py         # 資料儲存模組
├── .github/
│   └── workflows/
│       └── daily-monitor.yml  # GitHub Actions 設定
├── data/                   # 歷史資料（自動產生）
│   ├── market_history.json
│   └── stock_history.json
├── requirements.txt        # Python 套件需求
├── .env.example           # 環境變數範例
├── .gitignore            # Git 忽略檔案
├── README.md             # 說明文件
└── stock_monitor.log     # 執行記錄（自動產生）
```

---

## 📧 Email 報告範例

每日報告包含：

### 1️⃣ 大盤三大法人
- 今日買賣金額摘要
- 大額交易警示
- 連續買賣趨勢

### 2️⃣ 個股分析
- 超大額交易警示（≥1.5億）
- 大額交易提醒（≥0.5億）
- 連續買超排行
- 連續賣超排行

---

## 🔧 進階使用

### 自訂執行時間

編輯 `.github/workflows/daily-monitor.yml`：

```yaml
on:
  schedule:
    # 台灣時間晚上 7 點（UTC 11:00）
    - cron: '0 11 * * *'
    
    # 每天早上 9 點和晚上 6 點
    - cron: '0 1,10 * * *'
```

### 使用 cron（Linux/macOS）

```bash
# 編輯 crontab
crontab -e

# 新增排程（每天晚上 6 點）
0 18 * * * cd /path/to/stock-monitor && /usr/bin/python3 main.py
```

### Docker 部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

---

## 🐛 常見問題

### Q1：為什麼沒收到 Email？

**檢查清單：**
1. ✅ 確認 `.env` 中的 `SMTP_USER` 和 `SMTP_PASSWORD` 正確
2. ✅ 檢查垃圾郵件資料夾
3. ✅ 查看 `stock_monitor.log` 是否有錯誤訊息
4. ✅ 測試 Gmail 應用程式密碼是否有效

### Q2：GitHub Actions 執行失敗

**可能原因：**
- Secrets 設定不完整
- 網路連線問題
- 證交所資料尚未更新

**解決方式：**
1. 檢查 Actions 執行記錄
2. 下載 execution-log artifact 查看詳細錯誤
3. 手動觸發測試

### Q3：如何查看歷史資料？

歷史資料儲存在 `data/` 目錄：
- `market_history.json` - 大盤歷史
- `stock_history.json` - 個股歷史

可以使用 Python 讀取：

```python
from modules.storage import DataStorage

storage = DataStorage()
history = storage.load_history()

# 大盤歷史
print(history['market'][:5])

# 特定股票歷史
stock_data = storage.get_stock_history('2330', days=30)
```

---

## 📊 資料來源

- [台灣證券交易所 - 三大法人買賣金額統計](https://www.twse.com.tw/rwd/zh/fund/BFI82U)
- [台灣證券交易所 - 三大法人買賣超彙總](https://www.twse.com.tw/rwd/zh/fund/T86)

---

## 🚀 未來規劃

- [ ] 技術分析指標整合
- [ ] LINE Notify 推播
- [ ] Telegram Bot 支援
- [ ] Web 儀表板
- [ ] 更多資料來源（興櫃、櫃買）
- [ ] AI 預測模型
- [ ] Discord Webhook 通知

---

## 📝 版本歷史

### v2.0.0 (2026-04-21)
- 🎉 Python 版本首次發布
- 📊 完整的三大法人資料抓取
- 📈 智慧分析與趨勢追蹤
- 📧 HTML Email 報告
- 🤖 GitHub Actions 支援
- 💾 JSON 格式資料儲存

---

## ⚖️ 授權與免責聲明

本專案採用 MIT 授權，僅供學習和參考使用。

**免責聲明：**
- 本系統提供的資訊僅供參考，不構成任何投資建議
- 投資有風險，決策請審慎評估
- 使用者應自行承擔所有投資風險
- 資料來源為台灣證券交易所，可能有延遲

---

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

1. Fork 此專案
2. 建立你的 Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit 你的變更 (`git commit -m 'Add some AmazingFeature'`)
4. Push 到 Branch (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

---

## 📧 聯絡方式

如有任何問題或建議，歡迎：
- 開 Issue
- 發送 PR
- Email: your-email@example.com

---

**如果這個專案對你有幫助，請給一個 ⭐️ Star！**

Made with ❤️ by Claude AI Assistant
