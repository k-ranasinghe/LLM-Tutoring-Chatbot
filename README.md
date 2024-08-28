# obo-tutor-chatbot

Develop an intelligent tutoring chatbot (Obo Tutor) powered by large language models to provide personalised instruction and support to students of the RoboticGen Academy. The data used will be the knowledge base tailored to the RoboticGen Academy curriculum, incorporating all relevant topics and concepts. Building a custom chatbot using LLMs will require employing RAG framework and fine tuning with the incorporation of the tailored knowledge base


# Setup

Frontend Web App
```sh
cd client
npm install
npm start
```

Backend Web App
```sh
cd model
python -m venv venv
venv/Scripts/activate
pip install -r requirements.txt
uvicorn server:app --reload
```

Frontend Admin
```sh
cd admin/frontend
npm install
npm run dev
```

Backend Admin
```sh
cd admin
python -m venv venv
venv/Scripts/activate
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Backend Whatsapp
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
ngrok http 8000
```

Then add the ngrok url to twilio sandbox with "POST" method