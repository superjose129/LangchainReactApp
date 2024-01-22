# LangChainReactChatApp

LangChainでアプリを作成するときのひな形として、Flask + React + Dockerで単純なチャットアプリを作成しました。

# 動かし方
python(Flask + LangChain)とReactの開発・動作用のコンテナをbuildし起動します。  
LangChainを動かすためにOpenAIのAPI Keyが必要です。  

```
# python(Flask + LangChain)用コンテナのbuild
docker build -t lc-python -f python/Dockerfile .

# python(Flask + LangChain)用コンテナの起動
# OPENAI_API_KEYにOpenAIのAPI Keyを指定
docker run --rm -it -e OPENAI_API_KEY=${OPENAI_API_KEY} -v $(pwd)/python:/python -p 8080:8080 lc-python python app.py

# React用コンテナのbuild
docker build -t lc-react -f react/Dockerfile .

# React用コンテナのnpmパッケージをインストール
docker run --rm -it -p 5173:5173 -v $(pwd)/react:/react lc-react bash -c "cd app && yarn install"

# React用コンテナの起動
# VITE_API_ENDPOINTにはpython(Flask + LangChain)用コンテナを指定
docker run --rm -it -p 5173:5173 -v $(pwd)/react:/react -e VITE_API_ENDPOINT=http://localhost:8080 lc-react bash -c "cd app && yarn dev --host 0.0.0.0"
```

python(Flask + LangChain)とReactのコンテナを起動が完了すればブラウザのhttp://localhost:5173/からチャットアプリにアクセスできます。
