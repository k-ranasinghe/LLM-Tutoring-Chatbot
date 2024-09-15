from django.shortcuts import render
from twilio.rest import Client
from django.views.decorators.csrf import csrf_exempt
from django.http.response import HttpResponse
from dotenv import load_dotenv
from .app import run_model
from .ChatStoreSQL import update_personalization_params, get_personalization_params, get_past_chats, get_chat_ids
from .FileProcess import process_file
import os
import random
import string
import requests
from requests.auth import HTTPBasicAuth
from groq import Groq

load_dotenv()
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)
client1 = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Function to generate random ChatID
def generate_random_string(length, past_chats):
    charset = string.ascii_letters + string.digits
    while True:
        random_string = ''.join(random.choices(charset, k=length))
        if not any(chat == random_string for chat in past_chats):
            return random_string

@csrf_exempt
def bot(request):
    message = request.POST['Body'].strip()
    sender_name = request.POST['ProfileName']
    sender_number = request.POST['From']
    parameters = {"student_type": "type1", "learning_style": "Visual", "communication_format": "Textbook", "tone_style": "Neutral", "reasoning_framework": "Deductive"}
    print(message, sender_name, sender_number)
    # print(request.POST)

    past_chats = get_past_chats(sender_number)
    if not past_chats:
        # Fetch past chats
        all_chatid = get_chat_ids()
        chat_id = generate_random_string(10, all_chatid)
        update_personalization_params(chat_id, sender_number, "", parameters["learning_style"], parameters["communication_format"], parameters["tone_style"], parameters["reasoning_framework"])
    else:
        # Otherwise, pick the first chat's ChatID and Chat_title
        chat_id = past_chats[0]['ChatID']

    # Handling voice messages. Normal audio files are sent with the 'document' type which is handled seperately.
    if request.POST['MessageType'] == 'audio':
        media_url = request.POST['MediaUrl0']
        try:
            audio_response = requests.get(media_url, auth=HTTPBasicAuth(account_sid, auth_token))
                    
            if audio_response.status_code == 200:
                # Process the audio file as needed
                audio_file_path = 'uploads/received_audio.ogg'
                with open(audio_file_path, 'wb') as f:
                    f.write(audio_response.content)
                            
                print("Audio file downloaded successfully")
                response_message = f"Received audio message from {request.POST.get('From', '')}. Audio file downloaded."

                with open(audio_file_path, 'rb') as audio_file:
                    transcription = client1.audio.transcriptions.create(
                        file=audio_file,  # Use the file object directly
                        model="distil-whisper-large-v3-en",  # The required transcription model
                        prompt="Specify context or spelling",  # Optional prompt to guide transcription
                        response_format="json",  # Get response in JSON format
                        language="en",  # Specify language
                        temperature=0.0  # Set temperature for deterministic transcription
                    )
                        
                message = transcription.text
                print(message)

                extract = "No file attachments provided"
                response =run_model(chat_id, sender_number, message, extract)
                context_lines = "\n".join(response["context"])
                if response["context"] == []:
                    formatted_string = f"{response["response"]}"
                else:
                    formatted_string = f"*Voice Message Transcribed:*\n{message}\n\n*Response:*\n{response["response"]}\n\n\n*Recommended Resources:*\n\n{context_lines}"

                client.messages.create(
                        body=formatted_string,
                        from_='whatsapp:+14155238886',
                        to=sender_number, 
                )
                os.remove(audio_file_path)
            else:
                print(f"Failed to download audio file: {audio_response.status_code}")
                response_message = f"Failed to download audio file from {media_url}. Status code: {audio_response.status_code}"
        except Exception as e:
                    print(f"Error downloading audio file: {str(e)}")
                    response_message = f"Error downloading audio file: {str(e)}"
        return HttpResponse({'message': response_message})
        
    elif request.POST['MessageType'] == 'text':
        # Predefined command responses
        # Check if the message starts with "/"
        if message.startswith("/"):
            # Extract the command by removing the "/"
            command = message.split()[0][1:]

            # Handle specific commands
            if command == 'help':
                help_message = (
                    "Here are some commands you can use:\n"
                    "- `/help`: Shows available commands\n"
                    "- `/personalize`: Customize chatbot responses\n"
                    "- `/switch-chat`: Switch to another chat\n"
                    "- `/new-chat`: Start a new chat"
                )
                client.messages.create(
                    body=help_message,
                    from_='whatsapp:+14155238886',
                    to=sender_number
                )
                return HttpResponse("Help command executed")
            
            elif command == 'personalize':
                # If the message only contains "/personalize"
                if len(message.split()) == 1:
                    parameters = get_personalization_params(chat_id)
                    learning_style = parameters["learning_style"]
                    communication_format = parameters["communication_format"]
                    tone_style = parameters["tone_style"]
                    reasoning_framework = parameters["reasoning_framework"]
                    help_message = (
                        "Here are the current personalization parameter values:\n"
                        f"- *Learning Style* - {learning_style}\n"
                        f"- *Communication Format* - {communication_format}\n"
                        f"- *Tone Style* - {tone_style}\n"
                        f"- *Reasoning Framework* - {reasoning_framework}\n\n"
                        "Here are the available customizations:\n"
                        "- *Learning Style[1]* - Visual, Verbal, Active, Intuitive, Reflective\n"
                        "- *Communication Format[2]* - Textbook, Layman, Storytelling\n"
                        "- *Tone Style[3]* - Encouraging, Neutral, Informative, Friendly\n"
                        "- *Reasoning Framework[4]* - Deductive, Inductive, Abductive, Analogical\n\n"
                        "To update these parameters, use the following format:\n"
                        "`/personalize <parameter[ID]> <value>`\n\n"
                        "For example, to set the *Learning Style* to *Visual*, use:\n"
                        "`/personalize 1 Visual`\n"
                        
                    )
                    client.messages.create(
                        body=help_message,
                        from_='whatsapp:+14155238886',
                        to=sender_number
                    )
                    return HttpResponse("Personalize command executed")
                
                # If the message contains additional text in the format "/personalize <parameter> <value>"
                else:
                    try:
                        _, param_id, value = message.split(maxsplit=2)  # Extract ID and value
                        
                        # Mapping parameter IDs to their actual names
                        param_map = {
                            '1': 'learning_style',
                            '2': 'communication_format',
                            '3': 'tone_style',
                            '4': 'reasoning_framework'
                        }

                        # Validate the parameter ID
                        if param_id not in param_map:
                            raise ValueError("Invalid parameter ID")

                        # Get the actual parameter name from the map
                        parameter = param_map[param_id]

                        # Here, you'd update the personalization settings based on parameter and value
                        parameters = get_personalization_params(chat_id)
                        parameters[parameter] = value
                        update_personalization_params(chat_id, sender_number, parameters["chat_title"], parameters["learning_style"], parameters["communication_format"], parameters["tone_style"], parameters["reasoning_framework"])

                        success_message = f"Personalization updated: *{parameter}* set to *{value}*."
                        client.messages.create(
                            body=success_message,
                            from_='whatsapp:+14155238886',
                            to=sender_number
                        )
                        return HttpResponse("Personalization updated successfully")
                    
                    except ValueError:
                        error_message = "Invalid format or parameter ID. Please use: `/personalize <parameter[ID]> <value>`"
                        client.messages.create(
                            body=error_message,
                            from_='whatsapp:+14155238886',
                            to=sender_number
                        )
                        return HttpResponse("Invalid format")
                
            # switch-chat command to switch between existing user chats
            elif command == 'switch-chat':
                past_chats = get_past_chats(sender_number)
                command_parts = message.split()
                if len(command_parts) == 1:  # No ID provided after /switch-chat
                    # Construct a message showing available chat titles and timestamps
                    if past_chats:
                        available_chats_message = "Available Chats:\n"
                        i = 1
                        for chat in past_chats:
                            available_chats_message += f"*{i}* - {chat['Chat_title']} (Last active: {chat['Timestamp']})\n"
                            i += 1

                        available_chats_message += "\nTo switch chat, use the following format:\n" + "`/switch-chat <ID>`"
                    else:
                        available_chats_message = "You have no past chats.\n"

                    # Send available chats or no chats message
                    client.messages.create(
                        body=available_chats_message,
                        from_='whatsapp:+14155238886',
                        to=sender_number
                    )
                    return HttpResponse("Available chats displayed")
                
                # If the user provides a chat ID after /switch-chat (e.g., /switch-chat 2)
                else:
                    # Chat ID provided
                    try:
                        chat_index = int(command_parts[1]) - 1  # Get chat index from user input
                        if 0 <= chat_index < len(past_chats):
                            selected_chat = past_chats[chat_index]
                            # Update the chat ID in your system (assuming you have a function to do this)
                            chat_id = selected_chat['ChatID']
                            parameters = get_personalization_params(chat_id)
                            update_personalization_params(chat_id, sender_number, parameters["chat_title"], parameters["learning_style"], parameters["communication_format"], parameters["tone_style"], parameters["reasoning_framework"])
                            
                            # Confirmation message
                            client.messages.create(
                                body=f"Switched to chat: {selected_chat['Chat_title']}",
                                from_='whatsapp:+14155238886',
                                to=sender_number
                            )
                            return HttpResponse("Chat switched successfully")
                        else:
                            raise IndexError("Invalid chat index")
                    except (ValueError, IndexError):
                        # Handle invalid chat index or non-numeric ID
                        client.messages.create(
                            body="Invalid chat ID. Please use a valid number corresponding to a chat.",
                            from_='whatsapp:+14155238886',
                            to=sender_number
                        )
                        return HttpResponse("Invalid chat ID provided")
            
            # new-chat command to start a new chat
            elif command == 'new-chat':
                command_parts = message.split()

                if len(command_parts) == 1:  # No confirmation provided
                    help_message = (
                        "*Confirm New Chat*\n"
                        "To start a new chat, use the following format:\n"
                        "`/new-chat confirm`"
                    )
                    client.messages.create(
                        body=help_message,
                        from_='whatsapp:+14155238886',
                        to=sender_number
                    )
                    return HttpResponse("New chat confirmation requested")
                
                # To create a new chat, the user must confirm with `/new-chat confirm`
                elif command_parts[1].lower() == 'confirm':  # User confirmed new chat
                    # Fetch all existing chat IDs to ensure the new one is unique
                    all_chatid = get_chat_ids()
                    chat_id = generate_random_string(10, all_chatid)
                    update_personalization_params(
                        chat_id,
                        sender_number,
                        "",  # Placeholder for chat title
                        parameters["learning_style"],
                        parameters["communication_format"],
                        parameters["tone_style"],
                        parameters["reasoning_framework"]
                    )
                    
                    # Send a message confirming the new chat creation
                    client.messages.create(
                        body=f"New chat created with Chat ID: {chat_id}",
                        from_='whatsapp:+14155238886',
                        to=sender_number
                    )
                    return HttpResponse("New chat created successfully")

                else:
                    # Invalid format, return error message
                    client.messages.create(
                        body="Invalid command format. To start a new chat, use:\n`/new-chat confirm`",
                        from_='whatsapp:+14155238886',
                        to=sender_number
                    )
                    return HttpResponse("Invalid command format")
            
            # Handle unknown commands
            else:
                unknown_command_message = f"The command '{command}' is not recognized. Type /help for available commands."
                client.messages.create(
                    body=unknown_command_message,
                    from_='whatsapp:+14155238886',
                    to=sender_number
                )
                return HttpResponse("Unknown command")

        # If the message does not start with "/", it is a regular chat message
        else :
            media_urls = [
                "https://www.geeky-gadgets.com/wp-content/uploads/2024/02/ChatGPT-alternative-Groq.jpg",  # Replace with your image URL
                "https://cdn.mos.cms.futurecdn.net/emJzqH4JermveVrtNC4BsZ.png"  # Replace with your document URL
            ]

            extract = "No file attachments provided"
            response =run_model(chat_id, sender_number, message, extract)
            context_lines = "\n".join(response["context"])
            if response["context"] == []:
                formatted_string = f"{response["response"]}"
            else:
                formatted_string = f"{response["response"]}\n\n\n*Recommended Resources:*\n\n{context_lines}"

            client.messages.create(
                    body=formatted_string,
                    from_='whatsapp:+14155238886',
                    to=sender_number,
                    # media_url=media_urls  
            )

            return HttpResponse("chatbot response sent")
        
    # Handling File inputs
    else:
        media_url = request.POST['MediaUrl0']
        media_type = request.POST['MediaContentType0']
        file_extension = media_type.split('/')[-1]
        media_type_category = media_type.split('/')[0]

        try:
            file_response = requests.get(media_url, auth=HTTPBasicAuth(account_sid, auth_token))
                    
            if file_response.status_code == 200:
                # Process the file as needed
                file_path = f'uploads/{media_type_category}.{file_extension}'
                with open(file_path, 'wb') as f:
                    f.write(file_response.content)
                            
                print(f"{media_type_category} file downloaded successfully")

                extract = process_file(file_path)
                print(extract)

                # If the message is empty, set a default message
                if message == "":
                    message = "explain the contents of the attached file"
                
                response = run_model(chat_id, sender_number, message, extract)
                context_lines = "\n".join(response["context"])
                if response["context"] == []:
                    formatted_string = f"{response["response"]}"
                else:
                    formatted_string = f"*User Query:*\n{message}\n\n*Response:*\n{response["response"]}\n\n\n*Recommended Resources:*\n\n{context_lines}"

                client.messages.create(
                        body=formatted_string,
                        from_='whatsapp:+14155238886',
                        to=sender_number, 
                )

                os.remove(file_path)
                response_message = f"Received media message from {request.POST.get('From', '')}. Media file downloaded."

        except Exception as e:
                    print(f"Error downloading audio file: {str(e)}")
                    response_message = f"Error downloading audio file: {str(e)}"
        return HttpResponse({'message': "response_message"})