from fastapi import Request, BackgroundTasks
from twilio.rest import Client
from groq import Groq
import os
from fastapi.responses import JSONResponse
import urllib.parse
import random
import string
import requests
from requests.auth import HTTPBasicAuth

from app import run_model
from FileProcess import process_file
from ChatStoreSQL import (update_personalization_params, get_personalization_params, get_past_chats, delete_chat,
                        get_chat_ids, load_chat_history, get_existing_feedback, get_mentor_notes)

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio = Client(account_sid, auth_token)
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Cache for preloading variables
preloaded_data = {}

# Function to generate random ChatID
def generate_random_string(length, past_chats):
    charset = string.ascii_letters + string.digits
    while True:
        random_string = ''.join(random.choices(charset, k=length))
        if not any(chat == random_string for chat in past_chats):
            return random_string

# Helper function to preload chat-specific data
async def preload_chat_data(ChatID):
    global preloaded_data
    if ChatID not in preloaded_data:
        preloaded_data[ChatID] = {}
        
    # Preload chat history and summary
    chat_history, chat_summary = load_chat_history(ChatID)
    preloaded_data[ChatID]["chat_history"] = chat_history if chat_history else []
    preloaded_data[ChatID]["chat_summary"] = chat_summary if chat_summary else ""

    # Preload personalization data
    preloaded_data[ChatID]["personalization"] = get_personalization_params(ChatID)

    print(f"Preloaded data for ChatID {ChatID}")

async def preload_user_data(UserID):
    global preloaded_data
    if UserID not in preloaded_data:
        preloaded_data[UserID] = {}
        
    # Preload mentor notes and feedback using UserID
    preloaded_data[UserID]["notes"] = get_mentor_notes(UserID)
    preloaded_data[UserID]["feedback"] = get_existing_feedback(UserID)

    print(f"Preloaded data for UserID {UserID}")

async def update_preload_data(ChatID):
    global preloaded_data
    if ChatID not in preloaded_data:
        preloaded_data[ChatID] = {}
        
    # Preload chat history and summary
    chat_history, chat_summary = load_chat_history(ChatID)
    preloaded_data[ChatID]["chat_history"] = chat_history if chat_history else []
    preloaded_data[ChatID]["chat_summary"] = chat_summary if chat_summary else ""

    print(f"Updated chat history and chat summary for ChatID {ChatID}")

async def remove_file(file):
    try:
        os.remove(file)
    except OSError as e:
        return JSONResponse(content={"error": f"Error removing file: {e}"}, status_code=500)

async def fetch_resources(preloaded_data, ChatID, sender_number):
    chat_history = preloaded_data[ChatID]["chat_history"]
    msg = chat_history[-1]
    context = msg.response_metadata["context"]

    if context and any(context.values()):
        # Formatting the context for WhatsApp message
        message_body = "Recommended Resources 📚:\n\n"
        emoji = ["🔎", "🎥"]
        i=0
        for category, links in context.items():
            message_body += f"*{category} {emoji[i]}:*\n"
            for link in links:
                message_body += f"• {link}\n"
            message_body += "\n"
            i =+1

        # Sending the message
        twilio.messages.create(
            body=message_body.strip(),
            from_='whatsapp:+14155238886',
            to=sender_number,
        )
    else:
        print("No resources available to send.")

async def whatsapp(request: Request, background_tasks: BackgroundTasks):
    # Read the raw body
    raw_body = await request.body()
    
    # Decode the bytes to string
    body_as_str = raw_body.decode("utf-8")

    # Parse the URL-encoded form data into a dictionary
    parsed_data = urllib.parse.parse_qs(body_as_str)

    # Extract the desired information
    message = parsed_data.get('Body', [''])[0].strip()  # Default to empty string if not found
    sender_name = parsed_data.get('ProfileName', [''])[0]
    sender_number = parsed_data.get('From', [''])[0]
    msg_type = parsed_data.get('MessageType', [''])[0]

    # Print the extracted information for debugging
    print("Message:", message)
    print("Sender Name:", sender_name)
    print("Sender Number:", sender_number)
    
    parameters = {"student_type": "type1", "learning_style": "Visual", "communication_format": "Textbook", "tone_style": "Neutral", "reasoning_framework": "Deductive"}
    past_chats = get_past_chats(sender_number)
    if not past_chats:
        # Fetch past chats
        all_chatid = get_chat_ids()
        chat_id = generate_random_string(10, all_chatid)
        update_personalization_params(chat_id, sender_number, "", parameters["learning_style"], parameters["communication_format"], parameters["tone_style"], parameters["reasoning_framework"])
    else:
        # Otherwise, pick the first chat's ChatID and Chat_title
        chat_id = past_chats[0]['ChatID']
    
    if chat_id not in preloaded_data:
            await preload_chat_data(chat_id)
    if sender_number not in preloaded_data:
            await preload_user_data(sender_number)
            
    
    # Handling voice messages. Normal audio files are sent with the 'document' type which is handled seperately.
    if msg_type == 'audio':
        media_url = parsed_data.get('MediaUrl0', [''])[0]
        try:
            audio_response = requests.get(media_url, auth=HTTPBasicAuth(account_sid, auth_token))
                    
            if audio_response.status_code == 200:
                # Process the audio file as needed
                audio_file_path = 'uploads/received_audio.ogg'
                with open(audio_file_path, 'wb') as f:
                    f.write(audio_response.content)
                            
                print("Audio file downloaded successfully")
                response_message = f"Received audio message from {parsed_data.get('From', [''])[0]}. Audio file downloaded."

                with open(audio_file_path, 'rb') as audio_file:
                    transcription = client.audio.transcriptions.create(
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
                response = run_model(chat_id, sender_number, message, extract, "text", "text", preloaded_data, background_tasks)
                context_lines = "\n".join(response["context"])
                if response["context"] == []:
                    formatted_string = f"{response["response"]} 😇"
                else:
                    formatted_string = f"*🎤 Voice Message Transcribed:*\n{message}\n\n*Response:*\n{response["response"]}"

                twilio.messages.create(
                        body=formatted_string,
                        from_='whatsapp:+14155238886',
                        to=sender_number, 
                )
                
                remove_response = await remove_file(audio_file_path)
                if remove_response:
                    return remove_response
                background_tasks.add_task(update_preload_data, chat_id)
                background_tasks.add_task(fetch_resources, chat_id, sender_number)
            else:
                print(f"Failed to download audio file: {audio_response.status_code}")
                response_message = f"Failed to download audio file from {media_url}. Status code: {audio_response.status_code}"
        except Exception as e:
                    print(f"Error downloading audio file: {str(e)}")
                    response_message = f"Error downloading audio file: {str(e)}"
        return JSONResponse({'message': response_message})
        
    elif msg_type == 'text':
        # Predefined command responses
        # Check if the message starts with "/"
        if message.startswith("/"):
            # Extract the command by removing the "/"
            command = message.split()[0][1:]

            # Handle specific commands
            if command == 'help':
                help_message = (
                    "Here are some commands you can use:\n"
                    "🆘 `/help`: Shows available commands\n"
                    "🎨 `/personalize`: Customize chatbot responses\n"
                    "🔄 `/switch-chat`: Switch to another chat\n"
                    "🆕 `/new-chat`: Start a new chat\n"
                    "🗑️ `/delete-chat`: Delete a chat"
                )
                twilio.messages.create(
                    body=help_message,
                    from_='whatsapp:+14155238886',
                    to=sender_number
                )
                return JSONResponse("Help command executed")
            
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
                        f"- 🧠 *Learning Style* - {learning_style}\n"
                        f"- 📚 *Communication Format* - {communication_format}\n"
                        f"- 🎤 *Tone Style* - {tone_style}\n"
                        f"- 🧩 *Reasoning Framework* - {reasoning_framework}\n\n"
                        "Here are the available customizations:\n"
                        "- 🧠 *Learning Style[1]* - Visual, Verbal, Active, Intuitive, Reflective\n"
                        "- 📚 *Communication Format[2]* - Textbook, Layman, Storytelling\n"
                        "- 🎤 *Tone Style[3]* - Encouraging, Neutral, Informative, Friendly\n"
                        "- 🧩 *Reasoning Framework[4]* - Deductive, Inductive, Abductive, Analogical\n\n"
                        "To update these parameters, use the following format:\n"
                        "`/personalize <parameter[ID]> <value>`\n\n"
                        "For example, to set the *Learning Style* to *Visual*, use:\n"
                        "`/personalize 1 Visual`\n"
                        
                    )
                    twilio.messages.create(
                        body=help_message,
                        from_='whatsapp:+14155238886',
                        to=sender_number
                    )
                    return JSONResponse("Personalize command executed")
                
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

                        success_message = f"Personalization updated: *{parameter}* set to *{value}* 💫"
                        twilio.messages.create(
                            body=success_message,
                            from_='whatsapp:+14155238886',
                            to=sender_number
                        )
                        
                        background_tasks.add_task(preload_chat_data, chat_id)
                        
                        return JSONResponse("Personalization updated successfully")
                    
                    except ValueError:
                        error_message = "❌ Invalid format or parameter ID. Please use: `/personalize <parameter[ID]> <value>`"
                        twilio.messages.create(
                            body=error_message,
                            from_='whatsapp:+14155238886',
                            to=sender_number
                        )
                        return JSONResponse("Invalid format")
                
            # switch-chat command to switch between existing user chats
            elif command == 'switch-chat':
                past_chats = get_past_chats(sender_number)
                command_parts = message.split()
                if len(command_parts) == 1:  # No ID provided after /switch-chat
                    # Construct a message showing available chat titles and timestamps
                    if past_chats:
                        available_chats_message = "🗒️ *Available Chats:*\n"
                        i = 1
                        for chat in past_chats:
                            available_chats_message += f"*{i}* - {chat['Chat_title']} (Last active: {chat['Timestamp']})\n"
                            i += 1

                        available_chats_message += "\nTo switch chat, use the following format:\n" + "`/switch-chat <ID>`"
                    else:
                        available_chats_message = "You have no past chats.\n"

                    # Send available chats or no chats message
                    twilio.messages.create(
                        body=available_chats_message,
                        from_='whatsapp:+14155238886',
                        to=sender_number
                    )
                    return JSONResponse("Available chats displayed")
                
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
                            twilio.messages.create(
                                body=f"Switched to chat: {selected_chat['Chat_title']} 💫",
                                from_='whatsapp:+14155238886',
                                to=sender_number
                            )
                            
                            background_tasks.add_task(preload_chat_data, chat_id)
                            
                            return JSONResponse("Chat switched successfully")
                        else:
                            raise IndexError("Invalid chat index")
                    except (ValueError, IndexError):
                        # Handle invalid chat index or non-numeric ID
                        twilio.messages.create(
                            body="❌ Invalid chat ID. Please use a valid number corresponding to a chat.",
                            from_='whatsapp:+14155238886',
                            to=sender_number
                        )
                        return JSONResponse("Invalid chat ID provided")
            
            # new-chat command to start a new chat
            elif command == 'new-chat':
                command_parts = message.split()

                if len(command_parts) == 1:  # No confirmation provided
                    help_message = (
                        "*🆕 Confirm New Chat*\n"
                        "To start a new chat, use the following format:\n"
                        "`/new-chat confirm`"
                    )
                    twilio.messages.create(
                        body=help_message,
                        from_='whatsapp:+14155238886',
                        to=sender_number
                    )
                    return JSONResponse("New chat confirmation requested")
                
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
                    twilio.messages.create(
                        body=f"New chat created with Chat ID: {chat_id} 💫",
                        from_='whatsapp:+14155238886',
                        to=sender_number
                    )
                    background_tasks.add_task(preload_chat_data, chat_id)
                    background_tasks.add_task(preload_user_data, sender_number)
                    
                    return JSONResponse("New chat created successfully")

                else:
                    # Invalid format, return error message
                    twilio.messages.create(
                        body="❌ Invalid command format. To start a new chat, use:\n`/new-chat confirm`",
                        from_='whatsapp:+14155238886',
                        to=sender_number
                    )
                    return JSONResponse("Invalid command format")
            
            # delete-chat command to delete a existing chat
            elif command == 'delete-chat':
                past_chats = get_past_chats(sender_number)
                command_parts = message.split()
                if len(command_parts) == 1:  # No ID provided after /switch-chat
                    # Construct a message showing available chat titles and timestamps
                    if past_chats:
                        available_chats_message = "🗒️ *Available Chats:*\n"
                        i = 1
                        for chat in past_chats:
                            available_chats_message += f"*{i}* - {chat['Chat_title']} (Last active: {chat['Timestamp']})\n"
                            i += 1

                        available_chats_message += "\nTo delete chat, use the following format:\n" + "`/delete-chat <ID>`"
                    else:
                        available_chats_message = "You have no past chats.\n"

                    # Send available chats or no chats message
                    twilio.messages.create(
                        body=available_chats_message,
                        from_='whatsapp:+14155238886',
                        to=sender_number
                    )
                    return JSONResponse("Available chats displayed")
                
                # If the user provides a chat ID after /deleteswitch-chat (e.g., /delete-chat 2)
                else:
                    # Chat ID provided
                    try:
                        chat_index = int(command_parts[1]) - 1  # Get chat index from user input
                        if 0 <= chat_index < len(past_chats):
                            selected_chat = past_chats[chat_index]
                            # Update the chat ID in your system (assuming you have a function to do this)
                            chatID = selected_chat['ChatID']
                            delete_chat(chatID)
                            
                            # Confirmation message
                            twilio.messages.create(
                                body=f"Deleted chat: {selected_chat['Chat_title']} 💫",
                                from_='whatsapp:+14155238886',
                                to=sender_number
                            )
                            
                            background_tasks.add_task(preload_user_data, sender_number)
                            
                            return JSONResponse("Chat deleted successfully")
                        else:
                            raise IndexError("Invalid chat index")
                    except (ValueError, IndexError):
                        # Handle invalid chat index or non-numeric ID
                        twilio.messages.create(
                            body="❌ Invalid chat ID. Please use a valid number corresponding to a chat.",
                            from_='whatsapp:+14155238886',
                            to=sender_number
                        )
                        return JSONResponse("Invalid chat ID provided")
            
            # Handle unknown commands
            else:
                unknown_command_message = f"🤓 The command '{command}' is not recognized. Type `/help` for available commands."
                twilio.messages.create(
                    body=unknown_command_message,
                    from_='whatsapp:+14155238886',
                    to=sender_number
                )
                return JSONResponse("Unknown command")

        # If the message does not start with "/", it is a regular chat message
        else :
            media_urls = [
                "https://www.geeky-gadgets.com/wp-content/uploads/2024/02/ChatGPT-alternative-Groq.jpg",  # Replace with your image URL
                "https://cdn.mos.cms.futurecdn.net/emJzqH4JermveVrtNC4BsZ.png"  # Replace with your document URL
            ]

            extract = "No file attachments provided"
            response = run_model(chat_id, sender_number, message, extract, "text", "text", preloaded_data, background_tasks)
            context_lines = "\n".join(response["context"])
            if response["context"] == []:
                formatted_string = f"{response["response"]} 😇"
            else:
                formatted_string = f"{response["response"]}"

            twilio.messages.create(
                    body=formatted_string,
                    from_='whatsapp:+14155238886',
                    to=sender_number,
                    # media_url=media_urls  
            )
            
            background_tasks.add_task(update_preload_data, chat_id)
            background_tasks.add_task(fetch_resources, preloaded_data, chat_id, sender_number)

            return JSONResponse("chatbot response sent")
        
    # Handling File inputs
    else:
        media_url = parsed_data.get('MediaUrl0', [''])[0]
        media_type = parsed_data.get('MediaContentType0', [''])[0]
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

                extract = process_file(file_path, message, background_tasks)
                print(extract)

                # If the message is empty, set a default message
                if message == "":
                    message = "Explain the contents of the attached file."
                
                filename = f'{media_type_category}.{file_extension}'
                response = run_model(chat_id, sender_number, message, extract, media_type_category, filename, preloaded_data, background_tasks)
                context_lines = "\n".join(response["context"])
                if response["context"] == []:
                    formatted_string = f"{response["response"]} 😇"
                elif parsed_data.get('Body', [''])[0].strip() == "":
                    formatted_string = f"*User Query:*\n{message} 🔗\n\n*Response:*\n{response["response"]}"
                else:
                    formatted_string = f"{response["response"]}"

                twilio.messages.create(
                        body=formatted_string,
                        from_='whatsapp:+14155238886',
                        to=sender_number, 
                )

                os.remove(file_path)
                response_message = f"Received media message from {parsed_data.get('From', [''])[0]}. Media file downloaded."

        except Exception as e:
                    print(f"Error downloading file: {str(e)}")
                    response_message = f"Error downloading file: {str(e)}"
        
        background_tasks.add_task(update_preload_data, chat_id)
        background_tasks.add_task(fetch_resources, preloaded_data, chat_id, sender_number)
        
        return JSONResponse({'message': response_message})