# Streamlit 教學 - 韭菜計算機 🌱

**[🎧 線上demo](https://stock-yoyo.streamlit.app/)**

* [Youtube Tutorial - Streamlit 教學, 搭配 Pyenv, UV 高效開發](https://youtu.be/cH1pb_o7EPA)

如果你想要建立簡單的 python 程式, 又想呈現一些資料, 非常適合使用這個 😀

這個範例是一個**台股韭菜計算機**, 幫你算買賣股票的手續費、證交稅與最後損益。

官方文件可參考 [https://docs.streamlit.io/develop](https://docs.streamlit.io/develop)

## 功能

* 💰 試算買賣股票的**券商手續費、證交稅、淨損益與報酬率**
* 🔀 支援**現股 / 當沖**（當沖證交稅減半）
* 🧩 支援**整股（張）與零股（股）**, 一張 = 1000 股, 零股最小 1 股
* 🎚️ 可調**券商折數**（例如 2.5 折）
* ⚙️ **進階設定**可自訂手續費率與證交稅率（不同券商、稅率政策調整都能對應）
* 🟢 醒目的**結果橫幅**（獲利綠 / 虧損紅, 標題顯示金額與報酬率）
* 📇 結果以 **metric 卡片**呈現（買入成本 / 賣出淨收 / 獲利＋報酬率, 賺綠賠紅）
* 📋 **費用明細表**, 一眼看清每一筆費用
* 📉 **損益平衡圖**（Altair）: 賺賠區上色、標出損益兩平點與你的賣價、零界線
* 🔗 輸入會**同步到網址**, 算完可直接複製連結分享
* 🎨 自訂主題（韭菜綠, 深色 / 淺色模式都看得清楚）

## 環境需求

* Python 3.13
* Streamlit >= 1.58（見 `requirements.txt`）

## 安裝

二選一即可。

**方法一: Pyenv + pip**

```bash
# 建立虛擬環境 (Python 版本可依需求調整)
pyenv virtualenv 3.13.13 streamlit
pyenv activate streamlit

# 安裝套件
pip install -r requirements.txt
```

**方法二: uv（更快）**

```bash
uv venv
uv pip install -r requirements.txt
```

## 執行

```bash
streamlit run streamlit_app.py
```

啟動後瀏覽器會自動打開 預設 http://localhost:8501

畫面

![alt tag](https://cdn.imgpile.com/f/VxP45ET_xl.png)

![alt tag](https://cdn.imgpile.com/f/3jCpYyz_xl.png)

## 使用 Docker 執行

參考 [Streamlit 官方 Docker 教學](https://docs.streamlit.io/deploy/tutorials/docker)。
本專案已附上 `Dockerfile`、`.dockerignore` 與 `docker-compose.yml`。

```bash
docker compose up -d --build
```

啟動後瀏覽器打開 http://localhost:8501 即可

## 使用 HTTPS（Caddy 反向代理）

本專案用 [Caddy](https://caddyserver.com/) 自動申請與續期憑證。設定就寫在**同一個 `docker-compose.yml`** 裡，
透過 Compose 的 `profiles` 切換：平常 `docker compose up` 只會啟動 app，加上 `--profile https` 才會把 Caddy 帶起來。

**設定網域（用 `.env`）**

網域是用環境變數 `DOMAIN` 帶給 Caddy。專案附了 `.env.example` 範本，請自己複製一份成 `.env` 再修改：

```bash
cp .env.example .env
# 編輯 .env, 把 DOMAIN 改成你的網域 (例如 DOMAIN=your-domain.com)
```

**正式環境**（已備妥 `.env` 與 DNS）:

```bash
docker compose --profile https up -d --build
```

Caddy 會自動跟 Let's Encrypt 申請正式憑證，瀏覽器打開 `https://your-domain.com` 即可。

**本機測試**（不設 `DOMAIN`, 預設 `localhost`, Caddy 用內建 CA 簽自簽憑證）:

```bash
docker compose --profile https up -d --build
# 瀏覽器開 https://localhost （自簽憑證會跳安全警告, 屬正常）
```

停止與清除（記得帶 `--profile https` 才會一起關掉 Caddy）:

```bash
docker compose --profile https down
```

說明:

* HTTP（80）會自動 308 轉向 HTTPS（443）。
* 對外走 Caddy；Caddy 透過 compose 內網以 `app:8501` 連到 Streamlit。
* Caddy 的 `reverse_proxy` 預設正確轉發 WebSocket（Streamlit 需要），不必額外設定。
* 憑證存在 `caddy_data` volume，重啟不會重新申請（避免撞 Let's Encrypt 速率限制）。
* 正式部署若不想讓 8501 也對外，可把 `app` 的 `ports` 改成 `127.0.0.1:8501:8501` 或整段移除（Caddy 仍能透過內網連到）。

## 佈署

佈署教學, 免費佈署(免費版只可以設定 public), 需要連結 github,

可以直接連結 github repo [佈署](https://docs.streamlit.io/deploy),

或是使用 codebase 去撰寫 code 可參考 [stock-yoyo repo](https://github.com/blue-rubiks/stock-yoyo),

這個其實就是用 devcontainer

(寫完 code 記得要 commit push 才會生效 😁 它會在你的 github 底下建立一個 repo),

devcontainer 可參考之前 [Vscode Dev Containers 教學](https://github.com/twtrubiks/vscode_python_note/tree/master?tab=readme-ov-file#vscode-dev-containers-%E6%95%99%E5%AD%B8)

## Donation

文章都是我自己研究內化後原創，如果有幫助到您，也想鼓勵我的話，歡迎請我喝一杯咖啡 :laughing:

綠界科技ECPAY ( 不需註冊會員 )

![alt tag](https://payment.ecpay.com.tw/Upload/QRCode/201906/QRCode_672351b8-5ab3-42dd-9c7c-c24c3e6a10a0.png)

[贊助者付款](http://bit.ly/2F7Jrha)

歐付寶 ( 需註冊會員 )

![alt tag](https://i.imgur.com/LRct9xa.png)

[贊助者付款](https://payment.opay.tw/Broadcaster/Donate/9E47FDEF85ABE383A0F5FC6A218606F8)

## 贊助名單

[贊助名單](https://github.com/twtrubiks/Thank-you-for-donate)
