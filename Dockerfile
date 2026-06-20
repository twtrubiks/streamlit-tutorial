# 韭菜計算機 Streamlit Dockerfile
# 參考官方教學: https://docs.streamlit.io/deploy/tutorials/docker
# 與官方不同處: 官方用 git clone 抓範例, 這裡改成 COPY 本地專案檔案。

FROM python:3.13-slim

WORKDIR /app

# curl 給 HEALTHCHECK 用; build-essential 給少數需要編譯的套件用
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 先複製 requirements.txt 並安裝, 善用 Docker layer 快取
# (只要相依套件沒變, 改 app 程式碼時就不必重裝)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 再複製其餘專案檔案 (app 程式碼與 .streamlit 主題設定)
COPY . .

EXPOSE 8501

# 健康檢查: Streamlit 內建的健康檢查端點
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# 監聽 0.0.0.0 才能從容器外連進來
ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
