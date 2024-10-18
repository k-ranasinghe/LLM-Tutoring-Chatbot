from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

load_dotenv()
groq_api_key=os.getenv('GROQ_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')

model=ChatGroq(groq_api_key=groq_api_key, model_name="llama3-70b-8192")
# model=ChatOpenAI(openai_api_key=openai_api_key, model_name="gpt-4o-mini")

# Path to your downloaded service account JSON key file
SERVICE_ACCOUNT_FILE = 'google_credentials.json'
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Custom Search Engine ID
CSE_ID = os.getenv('CSE_ID')

def fetch_youtube_videos(query, max_results=3):
    """
    Fetch top YouTube video links related to the query using YouTube Data API.
    """
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    search_response = youtube.search().list(
        q=query,
        part='snippet',
        maxResults=max_results,
        type='video',
        videoCategoryId='27'  # Education category
    ).execute()

    videos = []
    for item in search_response['items']:
        video_title = item['snippet']['title']
        video_url = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
        videos.append(f"{video_title}: {video_url}")

    return videos

def google_search(query, num_results=3):
    # Load the credentials from the service account file
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/cse", "https://www.googleapis.com/auth/cloud-platform"]
    )

    # Build the custom search service
    service = build("customsearch", "v1", credentials=credentials)

    # Call the search API
    result = service.cse().list(q=query, cx=CSE_ID, num=num_results).execute()

    # Extract only the titles and links
    articles = []
    for item in result.get('items', []):
        title = item['title']
        link = item['link']
        articles.append(f"{title}: {link}")

    return articles

def generate_query(input_text, response, chat_history):
    
    prompt = ChatPromptTemplate.from_messages([
        ("human", """
        **Conversation History**: {chat_history}
        **User Query:** {input_text}
        **Chatbot Response:** {response}
        
        Using the provided context, generate a concise web search query (15-25 words) to find relevant resources. 
        Prioritize recent messages in the chat history and provided user query and chatbot response. 
        Output only the search query without quotations or additional text.
        """)
    ])
    chain = LLMChain(llm=model, prompt=prompt)

    query = chain.invoke({"input_text": input_text, "response": response, "chat_history": chat_history})["text"]

    return query

def fetch_recommended_resources(input_text, response, chat_history):
    """
    This function fetches recommended resources like YouTube videos and web articles
    based on the search_query.
    """
    # Use the response or input_text for the search
    search_query = generate_query(input_text, response, chat_history)
    print(search_query)

    # Get recommended YouTube videos
    youtube_videos = fetch_youtube_videos(search_query)

    # Get recommended web articles
    web_articles = google_search(search_query)

    # Combine and return all resources
    resources = {
        "YouTube Videos": youtube_videos,
        "Web Articles": web_articles,
    }

    return resources