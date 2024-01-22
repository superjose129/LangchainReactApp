FROM python:3.8-buster

# ホストマシンのコードをコンテナにコピー
COPY ./python /python
WORKDIR /python/src

# 依存関係のインストール
RUN pip install --no-cache-dir -r requirements.txt