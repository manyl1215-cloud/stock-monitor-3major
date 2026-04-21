# 🚀 快速開始指南

## 🎯 目標

5 分鐘內在 GitHub 上設定好自動執行的三大法人監測系統！

---

## 📋 準備工作

你需要：
- ✅ GitHub 帳號
- ✅ Gmail 帳號（用於發送報告）

---

## 🔧 步驟 1：Fork 專案（30 秒）

1. 前往專案頁面（你現在看到的地方）
2. 點選右上角的 **「Fork」** 按鈕
3. 等待 Fork 完成

---

## 🔑 步驟 2：設定 Gmail 應用程式密碼（2 分鐘）

### 2.1 啟用兩步驟驗證

1. 前往 [Google 帳戶](https://myaccount.google.com/)
2. 左側選單：**安全性**
3. 找到「登入 Google」區塊
4. 點選 **兩步驟驗證** → 按照指示完成設定

### 2.2 產生應用程式密碼

1. 回到「安全性」頁面
2. 頁面底部：點選 **應用程式密碼**
3. 選擇應用程式：**郵件**
4. 選擇裝置：**其他（自訂名稱）**
5. 輸入名稱：**股市監測**
6. 點選 **產生**
7. **複製產生的 16 碼密碼**（重要！）

---

## 🔐 步驟 3：設定 GitHub Secrets（2 分鐘）

1. 進入你 Fork 的專案
2. 點選 **Settings**（設定）
3. 左側選單：**Secrets and variables** > **Actions**
4. 點選 **New repository secret**

### 新增以下 4 個 Secrets：

| 點選「New repository secret」→ 輸入 Name 和 Value |
|---------------------------------------------------|

#### Secret 1: EMAIL_TO
```
Name: EMAIL_TO
Value: manyl1215@gmail.com
```
**說明：** 收件人 Email（你的信箱）

#### Secret 2: SMTP_USER
```
Name: SMTP_USER
Value: your-gmail@gmail.com
```
**說明：** 你的 Gmail 帳號

#### Secret 3: SMTP_PASSWORD
```
Name: SMTP_PASSWORD
Value: (貼上步驟2的16碼密碼)
```
**說明：** Gmail 應用程式密碼（步驟 2 產生的）

#### Secret 4: WATCH_LIST (可選)
```
Name: WATCH_LIST
Value: 2330,2317,2454
```
**說明：** 要監測的股票代號（逗號分隔，留空則監測所有）

---

## ▶️ 步驟 4：啟用 GitHub Actions（30 秒）

1. 點選 **Actions** 標籤
2. 如果看到提示，點選 **「I understand my workflows, go ahead and enable them」**
3. 等待啟用完成

---

## 🧪 步驟 5：測試執行（1 分鐘）

1. 在 **Actions** 頁面
2. 左側選單：點選 **三大法人監測系統**
3. 右側點選 **Run workflow** 下拉選單
4. 點選綠色的 **Run workflow** 按鈕
5. 等待執行（約 30 秒 - 1 分鐘）

### 檢查結果

- ✅ **綠色勾勾**：成功！檢查你的信箱
- ❌ **紅色叉叉**：失敗，點進去查看錯誤訊息

---

## 📧 步驟 6：檢查信箱

1. 打開你的信箱（EMAIL_TO 設定的信箱）
2. 搜尋「三大法人監測報告」
3. 找到了！🎉

如果沒有收到：
- 檢查垃圾郵件資料夾
- 回到 Actions 查看執行記錄
- 確認 Secrets 設定正確

---

## ⏰ 自動執行設定

系統已經自動設定為：
- **每天晚上 6 點**（台灣時間）自動執行
- 自動抓取最新資料
- 自動發送報告到你的信箱

完全免費，無需任何伺服器！

---

## 🎨 進階設定（可選）

### 修改執行時間

編輯 `.github/workflows/daily-monitor.yml`：

```yaml
on:
  schedule:
    # 台灣時間晚上 7 點（UTC+8 = 11:00 UTC）
    - cron: '0 11 * * *'
```

### 監測特定股票

在 Secrets 中設定 `WATCH_LIST`：

```
2330,2317,2454,2882,2412
```

### 調整警示門檻

Fork 後修改程式碼中的門檻設定即可。

---

## ❓ 常見問題

### Q: 為什麼沒收到 Email？

**檢查清單：**
1. Secrets 是否都設定正確？
2. Gmail 應用程式密碼是否正確？
3. 是否在垃圾郵件資料夾？
4. 查看 Actions 執行記錄是否有錯誤

### Q: 如何手動執行？

1. Actions > 三大法人監測系統
2. Run workflow > Run workflow

### Q: 如何停止自動執行？

1. Settings > Actions > General
2. 關閉「Allow all actions and reusable workflows」

或直接刪除 `.github/workflows/daily-monitor.yml`

---

## 🎉 完成！

恭喜！你已經成功設定三大法人監測系統！

從現在開始：
- ✅ 每天晚上 6 點自動執行
- ✅ 自動抓取最新資料
- ✅ 自動分析三大法人動向
- ✅ 精美 HTML 報告寄到你的信箱

**完全免費，永久運行！** 🚀

---

## 📞 需要幫助？

- 查看完整 [README.md](README.md)
- 開 [Issue](../../issues) 回報問題
- 參考 [Actions 執行記錄](../../actions)

---

**享受你的自動化投資助手吧！** 📊💰
