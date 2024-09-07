from django.shortcuts import render
from twilio.rest import Client
from django.views.decorators.csrf import csrf_exempt
from django.http.response import HttpResponse
from dotenv import load_dotenv
from .app import run_model
from .ChatStoreSQL import update_personalization_params, get_personalization_params, get_past_chats, get_chat_ids
import os
import random
import string

load_dotenv()
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)

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

    past_chats = get_past_chats(sender_number)
    if not past_chats:
        # Fetch past chats
        all_chatid = get_chat_ids()
        chat_id = generate_random_string(10, all_chatid)
        update_personalization_params(chat_id, sender_number, "", parameters["learning_style"], parameters["communication_format"], parameters["tone_style"], parameters["reasoning_framework"])
    else:
        # Otherwise, pick the first chat's ChatID and Chat_title
        chat_id = past_chats[0]['ChatID']


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
        
        else:
            unknown_command_message = f"The command '{command}' is not recognized. Type /help for available commands."
            client.messages.create(
                body=unknown_command_message,
                from_='whatsapp:+14155238886',
                to=sender_number
            )
            return HttpResponse("Unknown command")

    else :
        media_urls = [
            "https://www.geeky-gadgets.com/wp-content/uploads/2024/02/ChatGPT-alternative-Groq.jpg",  # Replace with your image URL
            "https://cdn.mos.cms.futurecdn.net/emJzqH4JermveVrtNC4BsZ.png"  # Replace with your document URL
        ]


        response =run_model(chat_id,sender_number,message)
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