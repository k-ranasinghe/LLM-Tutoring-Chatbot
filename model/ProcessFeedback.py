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
        For the above user query and AI response, the user has provide the following feedback; 
        **Rating:** {feedback}
        **Feedback text:** {feedbackText}
        Based on this information, review the AI response using the provided feedback.
        Given below is the previously provided feedback by the user:
        {existing_feedback}
        Generate a response in the format of an instruction to be provided to the model to learn from the user feedback.
        """)
    ])
    chain = LLMChain(llm=model, prompt=prompt)

    review = chain.invoke({"userQuery": userQuery, "response": response, "feedback": feedback, "feedbackText": feedbackText, "existing_feedback": existing_feedback})["text"]

    return review