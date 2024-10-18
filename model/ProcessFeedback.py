from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
groq_api_key=os.getenv('GROQ_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')

model=ChatGroq(groq_api_key=groq_api_key, model_name="llama3-70b-8192")
# model=ChatOpenAI(openai_api_key=openai_api_key, model_name="gpt-4o-mini")

def review_feedback(userQuery, response, feedback, feedbackText, existing_feedback):
    
    prompt = ChatPromptTemplate.from_messages([
        ("human", """
        **User Query:** {userQuery}
        **Chatbot Response:** {response}
        **Rating:** {feedback}
        **Feedback text:** {feedbackText}
        **Previous feedback:** {existing_feedback}
        
        Analyze the provided user query, chatbot response, and feedback. 
        If feedback text is empty, evaluate the response quality based on the query and response content. 
        Generate a concise instruction (under 100 words) for the model to improve based on this feedback. 
        Consider both current and previous feedback for a comprehensive learning approach.
        Append the new feedback to the existing feedback and analyze step by step and provide one instruction capturing everything.
        Focus solely on the instruction without additional commentary. Output only the instruction without any additional text.
        The output must be under 100 words.
        """)
    ])
    chain = LLMChain(llm=model, prompt=prompt)

    review = chain.invoke({"userQuery": userQuery, "response": response, "feedback": feedback, "feedbackText": feedbackText, "existing_feedback": existing_feedback})["text"]

    return review