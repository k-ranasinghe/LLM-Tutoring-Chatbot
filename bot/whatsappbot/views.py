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

    # if message == "Hi":
    client.messages.create(
            # body="Hi {}".format(sender_name),
            body=run_model(sender_number,sender_name,message),
            from_='whatsapp:+14155238886',
            to=sender_number
    )
    return HttpResponse("hello")