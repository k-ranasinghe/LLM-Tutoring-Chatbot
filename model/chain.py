from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import MessagesPlaceholder
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.query_constructor.base import (
    StructuredQueryOutputParser,
    get_query_constructor_prompt,
)
from langchain.retrievers.self_query.pinecone import PineconeTranslator
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo
from dotenv import load_dotenv
import os
from PromptEng import get_template

load_dotenv()
groq_api_key=os.getenv('GROQ_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')

def create_chain(vectorStore):
    model=ChatGroq(groq_api_key=groq_api_key, model_name="mixtral-8x7b-32768")
    # model=ChatOpenAI(openai_api_key=openai_api_key, model_name="gpt-4o-mini")
    chain = create_stuff_documents_chain(
        llm=model,
        prompt=get_template(),
    )


    # Define metadata field information
    metadata_field_info = [
        AttributeInfo(
            name="course",
            description='The course relevant to the document. You must pick one of "Programming", "3D Design" or "Other".',
            type="string",
        ),
        AttributeInfo(
            name="subject",
            description="The subject relevant to the document. One of 'Programming', 'Electronics', '3D Design', 'Manufacturing' or 'Other'.",
            type="string",
        ),
        # AttributeInfo(
        #     name="Scope",
        #     description="The scope of the document. One of 'Introduction', 'Basics', 'Lab Activity', 'Project' or 'Other'.",
        #     type="string",
        # ),
        # AttributeInfo(
        #     name="Difficulty_level",
        #     description="The difficulty level of the content, on a scale of 1-5",
        #     type="integer",
        # ),
    ]

    document_content_description = "Brief description of educational content"

    # Define examples for the query constructor
    examples = [
        {
            "user_query": "what is bubble sort?",
            "structured_request": "",
            # {
            #     "query": "bubble sort algorithm implementation and efficiency",
            #     "filter": "and(eq(\"course\", \"Programming\"), eq(\"subject\", \"Programming\"))",
            # },
            "data_source":"",
            # {
            #                 "content": "Lyrics of a song",
            #                 # "attributes": {
            #                 #     "course": {
            #                 #         "type": "string",
            #                 #         "description": "Name of the song artist"
            #                 #     },
            #                 #     "subject": {
            #                 #         "type": "integer",
            #                 #         "description": "Length of the song in seconds"
            #                 #     },
            #                 # }
            #             },
            "i": 0,
        },
        # {
        #     "user_query": "what is bubble sort?",
        #     "structured_request": {
        #                             "query": "bubble sort algorithm implementation and efficiency",
        #                             "filter": "and(eq(\"course\", \"Programming\"), eq(\"subject\", \"Programming\"))",
        #                         },
        #     "data_source":{
        #                     # "content": "Lyrics of a song",
        #                     # "attributes": {
        #                     #     "course": {
        #                     #         "type": "string",
        #                     #         "description": "Name of the song artist"
        #                     #     },
        #                     #     "subject": {
        #                     #         "type": "integer",
        #                     #         "description": "Length of the song in seconds"
        #                     #     },
        #                     # }
        #                 },
        #     "i": 1,
        # },
        # {
        #     "user_query": "what is bubble sort?",
        #     "structured_request": {
        #                             "query": "bubble sort algorithm implementation and efficiency",
        #                             "filter": "and(eq(\"course\", \"Programming\"), eq(\"subject\", \"Programming\"))",
        #                         },
        #     "data_source":{
        #                     # "content": "Lyrics of a song",
        #                     # "attributes": {
        #                     #     "course": {
        #                     #         "type": "string",
        #                     #         "description": "Name of the song artist"
        #                     #     },
        #                     #     "subject": {
        #                     #         "type": "integer",
        #                     #         "description": "Length of the song in seconds"
        #                     #     },
        #                     # }
        #                 },
        #     "i": 2,
        # },
        # {
        #     "user_query": "what is bubble sort?",
        #     "structured_request": {
        #                             "query": "bubble sort algorithm implementation and efficiency",
        #                             "filter": "and(eq(\"course\", \"Programming\"), eq(\"subject\", \"Programming\"))",
        #                         },
        #     "data_source":{
        #                     # "content": "Lyrics of a song",
        #                     # "attributes": {
        #                     #     "course": {
        #                     #         "type": "string",
        #                     #         "description": "Name of the song artist"
        #                     #     },
        #                     #     "subject": {
        #                     #         "type": "integer",
        #                     #         "description": "Length of the song in seconds"
        #                     #     },
        #                     # }
        #                 },
        #     "i": 3,
        # },
        # {
        #     "user_query": "what is bubble sort?",
        #     "structured_request": {
        #                             "query": "bubble sort algorithm implementation and efficiency",
        #                             "filter": "and(eq(\"course\", \"Programming\"), eq(\"subject\", \"Programming\"))",
        #                         },
        #     "data_source":{
        #                     # "content": "Lyrics of a song",
        #                     # "attributes": {
        #                     #     "course": {
        #                     #         "type": "string",
        #                     #         "description": "Name of the song artist"
        #                     #     },
        #                     #     "subject": {
        #                     #         "type": "integer",
        #                     #         "description": "Length of the song in seconds"
        #                     #     },
        #                     # }
        #                 },
        #     "i": 4,
        # },
        # {
        #     "user_query": "what is bubble sort?",
        #     "structured_request": {
        #                             "query": "bubble sort algorithm implementation and efficiency",
        #                             "filter": "and(eq(\"course\", \"Programming\"), eq(\"subject\", \"Programming\"))",
        #                         },
        #     "data_source":{
        #                     # "content": "Lyrics of a song",
        #                     # "attributes": {
        #                     #     "course": {
        #                     #         "type": "string",
        #                     #         "description": "Name of the song artist"
        #                     #     },
        #                     #     "subject": {
        #                     #         "type": "integer",
        #                     #         "description": "Length of the song in seconds"
        #                     #     },
        #                     # }
        #                 },
        #     "i": 5,
        # },
        # {
        #     "user_query": "what is bubble sort?",
        #     "structured_request": {
        #                             "query": "bubble sort algorithm implementation and efficiency",
        #                             "filter": "and(eq(\"course\", \"Programming\"), eq(\"subject\", \"Programming\"))",
        #                         },
        #     "data_source":{
        #                     # "content": "Lyrics of a song",
        #                     # "attributes": {
        #                     #     "course": {
        #                     #         "type": "string",
        #                     #         "description": "Name of the song artist"
        #                     #     },
        #                     #     "subject": {
        #                     #         "type": "integer",
        #                     #         "description": "Length of the song in seconds"
        #                     #     },
        #                     # }
        #                 },
        #     "i": 6,
        # }
    ]

    # Get the base retriever
    # base_retriever = vectorStore.as_retriever()
    # self_query_retriever = SelfQueryRetriever.from_llm(
    #     llm=model,
    #     vectorstore=vectorStore,
    #     document_contents=document_content_description,
    #     metadata_field_info=metadata_field_info,
    # )

    prompt = get_query_constructor_prompt(
        document_content_description,
        metadata_field_info,
        # examples=examples,
    )
    output_parser = StructuredQueryOutputParser.from_components()
    query_constructor = prompt | model | output_parser

    self_query_retriever = SelfQueryRetriever(
    query_constructor=query_constructor,
    vectorstore=vectorStore,
    structured_query_translator=PineconeTranslator(),
    )

    retriever_prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        ("human", "Given the above conversation, generate a search query to look up in order to get information relevant to the " +
                "conversation from the knowledge base. Additionally we are filtering the database for the most relevant vectors before " +
                "doing the similarity search. Filtering criteria are course[one of 'Programming', '3D Design' or 'Other'], and subject[one " +
                "of 'Programming', 'Electronics', '3D Design', 'Manufacturing' or 'Other']. Your response must contain the search query and the " +
                "filtering criteria. Do not include anything else."),
    ])


# , Scope[one of 'Introduction', 'Basics', 'Lab Activity', 'Project' or 'Other'], Difficulty_level[1-5]

    history_aware_retriever = create_history_aware_retriever(
        llm=model,
        retriever=self_query_retriever,
        prompt=retriever_prompt
    )

    retrieval_chain = create_retrieval_chain(
        history_aware_retriever,
        chain
    )

    return retrieval_chain