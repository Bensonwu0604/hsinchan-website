# 欣晨工業網站部署指南
## GitHub + Vercel + DNS 從 Wix 轉移至 www.hsinchan.com

---

## 總覽：同步更新機制

```
你修改檔案 → git push 到 GitHub → Vercel 自動偵測 → 30 秒內自動部署 → 網站更新
```

未來每次更新網站（包含修改 content.json 的 FAQ），只需：
1. 修改檔案並儲存
2. `git add -A && git commit -m "更新內容" && git push`
3. Vercel 自動完成部署

---

## STEP 1：建立 GitHub 帳號與 Repository

1. 前往 https://github.com → 登入或註冊帳號
2. 點右上角 **＋** → **New repository**
3. 設定：
   - **Repository name**: `hsinchan-website`（或任意名稱）
   - **Visibility**: `Private`（推薦，保護原始碼）
   - **不要**勾選 Initialize with README
4. 點 **Create repository**
5. GitHub 會顯示指令，複製類似下方的遠端 URL：
   ```
   https://github.com/你的帳號/hsinchan-website.git
   ```

---

## STEP 2：將本地 Git Repo 推送到 GitHub

在電腦開啟終端機（命令提示字元或 PowerShell），進入網頁資料夾：

```bash
cd "d:\CLAUDE\欣晨網頁"

# 連結到 GitHub（把下面的 URL 換成你的）
git remote add origin https://github.com/你的帳號/hsinchan-website.git

# 將分支改名為 main
git branch -M main

# 推送
git push -u origin main
```

> **若出現登入視窗** → 輸入 GitHub 帳號密碼，或使用 Personal Access Token

---

## STEP 3：建立 Vercel 帳號並連結 GitHub

1. 前往 https://vercel.com → 點 **Sign Up** → 選 **Continue with GitHub**
2. 授權 Vercel 存取 GitHub
3. 在 Vercel Dashboard → 點 **Add New Project**
4. 找到 `hsinchan-website` → 點 **Import**
5. 設定：
   - **Framework Preset**: 選 `Other`（純 HTML 靜態網站）
   - **Root Directory**: 保持 `./`（預設）
   - **Build Command**: 留空
   - **Output Directory**: 留空
6. 點 **Deploy** → 等待 30 秒，完成！
7. Vercel 會給一個預設網址（如 `hsinchan-website.vercel.app`）先確認網站正常

---

## STEP 4：在 Vercel 綁定自訂網域 www.hsinchan.com

1. Vercel Dashboard → 選你的專案 → **Settings** → **Domains**
2. 輸入 `www.hsinchan.com` → 點 **Add**
3. Vercel 會顯示需要設定的 DNS 記錄：

   | 類型 | 名稱 | 值 |
   |------|------|----|
   | `CNAME` | `www` | `cname.vercel-dns.com` |

   同時也加入裸域名重定向（讓 hsinchan.com 自動跳到 www.hsinchan.com）：

   | 類型 | 名稱 | 值 |
   |------|------|----|
   | `A` | `@` | `76.76.21.21` |

4. **記下這些 DNS 設定值**，下一步在 Wix 修改

---

## STEP 5：從 Wix 修改 DNS 設定（切換最關鍵的一步）

> ⚠️ 此步驟執行後，Wix 網站約 10 分鐘～48 小時後停止服務，由 Vercel 接管

### 5a. 進入 Wix DNS 管理

1. 登入 Wix → 點右上角帳號 → **管理網域**
2. 找到 `hsinchan.com` → 點 **管理** → **進階 DNS**

### 5b. 修改 DNS 記錄

**刪除**現有的 Wix 指向記錄（通常是 A 記錄或 CNAME）：
- 刪除 `@` (root) 的 A 記錄（原本指向 Wix）
- 刪除 `www` 的 CNAME 記錄（原本指向 Wix）

**新增** Vercel 的 DNS 記錄：
```
類型: A       名稱: @     值: 76.76.21.21         TTL: 3600
類型: CNAME   名稱: www   值: cname.vercel-dns.com TTL: 3600
```

### 5c. 確認生效

DNS 傳播需要 **10 分鐘 ～ 48 小時**（通常 1 小時內完成）。

確認方法：在瀏覽器輸入 https://www.hsinchan.com，若顯示新網站即完成。

---

## STEP 6：確認 SSL 憑證自動啟用

Vercel 會自動為你的網域申請並續期 Let's Encrypt SSL 憑證，無需任何操作。

在 Vercel Dashboard → **Settings** → **Domains** 確認看到 ✅ 綠色圖示即可。

---

## 日常更新流程（之後每次改網站）

### 方法一：電腦本地修改（推薦）

```bash
# 1. 修改任何檔案（例如 content.json 更新 FAQ）

# 2. 推送
cd "d:\CLAUDE\欣晨網頁"
git add -A
git commit -m "更新 FAQ 內容"
git push

# Vercel 自動在 30 秒內部署完成 ✓
```

### 方法二：直接在 GitHub 網頁編輯（最簡單）

1. 前往 https://github.com/你的帳號/hsinchan-website
2. 點 `content.json`（或任何檔案）
3. 點鉛筆圖示 **Edit this file**
4. 修改後點 **Commit changes**
5. Vercel 自動部署 ✓

> **特別適合**：只需要修改 FAQ 文字時，直接在 GitHub 網頁改 content.json 最方便

---

## 常見問題

**Q: Wix 的 Email 信箱（@hsinchan.com）會受影響嗎？**
A: 不會。Email 是透過 MX 記錄運作，只要不動 MX 記錄，收發信不受影響。

**Q: Vercel 免費嗎？**
A: 免費方案（Hobby）足夠企業官網使用：
- 100GB 流量/月
- 自訂網域
- 自動 HTTPS
- 無限次部署
- 全球 CDN

**Q: 可以先預覽再正式上線嗎？**
A: 可以。在 push 之前，每個 Pull Request 都會有獨立的預覽網址。或直接在本地用 Live Server 預覽。

**Q: 萬一新網站出問題，可以緊急回到 Wix 嗎？**
A: 可以。在 Wix DNS 管理把 A 記錄和 CNAME 改回 Wix 原本的值即可（記得備份 Wix 原本的 DNS 設定值）。

---

## 部署前最終確認清單

- [ ] GitHub repo 已建立並 push 完成
- [ ] Vercel 預覽網址（.vercel.app）網站顯示正常
- [ ] 已備份 Wix 原本的 DNS 記錄值（截圖保存）
- [ ] Vercel 已加入 www.hsinchan.com 並取得 DNS 設定值
- [ ] Wix DNS 已更新為 Vercel 的 A 記錄和 CNAME
- [ ] https://www.hsinchan.com 顯示新網站
- [ ] SSL 憑證（https://）正常

---

*本文件由 Claude Code 生成 — 欣晨工業有限公司*
