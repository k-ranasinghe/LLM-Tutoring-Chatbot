from django.shortcuts import render
from twilio.rest import Client
from django.views.decorators.csrf import csrf_exempt
from django.http.response import HttpResponse
from dotenv import load_dotenv
from .app import run_model
import os

load_dotenv()
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)

@csrf_exempt
def bot(request):
    message = request.POST['Body']
    sender_name = request.POST['ProfileName']
    sender_number = request.POST['From']

    print(message, sender_name, sender_number)

    media_urls = [
        "https://www.geeky-gadgets.com/wp-content/uploads/2024/02/ChatGPT-alternative-Groq.jpg",  # Replace with your image URL
        "https://cdn.mos.cms.futurecdn.net/emJzqH4JermveVrtNC4BsZ.png"  # Replace with your document URL
    ]

    response =run_model("abc1","user123",message)
    context_lines = "\n".join(response["context"])
    formatted_string = f"{response["response"]}\n\nRecommended Resources:\n{context_lines}"

    client.messages.create(
            body=formatted_string,
            from_='whatsapp:+14155238886',
            to=sender_number,
            media_url=media_urls  # Sending multiple media files
    )

    return HttpResponse("hello")