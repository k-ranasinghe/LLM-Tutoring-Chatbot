# obo-tutor-chatbot

Develop an intelligent tutoring chatbot (Obo Tutor) powered by large language models to provide personalised instruction and support to students of the RoboticGen Academy. The data used will be the knowledge base tailored to the RoboticGen Academy curriculum, incorporating all relevant topics and concepts. Building a custom chatbot using LLMs will require employing RAG framework and fine tuning with the incorporation of the tailored knowledge base

## .env File
Include inside model directory.
```sh
OPENAI_API_KEY=
GEMINI_API_KEY=
YOUTUBE_API_KEY=
LANGCHAIN_API_KEY=
GROQ_API_KEY=
PINECONE_API_KEY=
PINECONE_INDEX=
LANGCHAIN_PROJECT=

# Custom Search Engine ID
CSE_ID=

MYSQL_HOST=
MYSQL_USER=
MYSQL_PASSWORD=
MYSQL_DB=

TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
```

<br>Get the API keys for Gemini and YouTube from [here](https://console.cloud.google.com/apis/dashboard).<br><br>
Enable Custom Search API from [here](https://console.cloud.google.com/apis/dashboard). Create a service account and get the json file containing the credentials. Paste the file inside the model directory as `google_credentials.json`.<br><br>
Create a Custom Search Engine from [here](https://programmablesearchengine.google.com). Get the search engine id and add it as `CSE_ID` to the `.env` file.

## Setup

Frontend Web App (port=3000)
```sh
cd client
npm install
npm start
```

Backend Web App (port=8000)
```sh
cd model
python -m venv venv
venv/scripts/activate
pip install -r requirements.txt
uvicorn server:app --reload
```


Host Backend for whatsapp
```sh
ngrok http 8000
```

Then add the ngrok url to twilio sandbox with "POST" method
