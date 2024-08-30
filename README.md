# obo-tutor-chatbot

Develop an intelligent tutoring chatbot (Obo Tutor) powered by large language models to provide personalised instruction and support to students of the RoboticGen Academy. The data used will be the knowledge base tailored to the RoboticGen Academy curriculum, incorporating all relevant topics and concepts. Building a custom chatbot using LLMs will require employing RAG framework and fine tuning with the incorporation of the tailored knowledge base


# Setup

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
venv/Scripts/activate
pip install -r requirements.txt
uvicorn server:app --reload
```

Frontend Admin (port=3001)
```sh
cd admin/frontend
npm install
npm run dev
```

Backend Admin (port=8001)
```sh
cd admin
python -m venv venv
venv/Scripts/activate
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Backend Whatsapp (port=8002)
```sh
cd bot
python -m venv venv
venv/Scripts/activate
cd whatsappbot
pip install -r requirements.txt
cd ..
python manage.py migrate
python manage.py runserver
```

Host Backend for whatsapp
```sh
ngrok http 8002
```

Then add the ngrok url to twilio sandbox with "POST" method