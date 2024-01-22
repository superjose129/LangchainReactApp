 LangChainReactChatApp

As a template for creating an app with LangChain, I have developed a simple chat application using Flask + React + Docker.

How to Run
Build and launch containers for python (Flask + LangChain) and React.
To run LangChain, you will need an API Key from OpenAI.

# Build container for python (Flask + LangChain)
docker build -t lc-python -f python/Dockerfile .

# Launch container for python (Flask + LangChain)
# Specify your OpenAI API Key with OPENAI_API_KEY
docker run --rm -it -e OPENAI_API_KEY=${OPENAI_API_KEY} -v $(pwd)/python:/python -p 8080:8080 lc-python python app.py

# Build container for React
docker build -t lc-react -f react/Dockerfile .

# Install npm packages in the React container
docker run --rm -it -p 5173:5173 -v $(pwd)/react:/react lc-react bash -c "cd app && yarn install"

# Launch React container
# Specify the python (Flask + LangChain) container as VITE_API_ENDPOINT
docker run --rm -it -p 5173:5173 -v $(pwd)/react:/react -e VITE_API_ENDPOINT=http://localhost:8080 lc-react bash -c "cd app && yarn dev --host 0.0.0.0"
