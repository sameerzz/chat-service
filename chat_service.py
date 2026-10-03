from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage


# Load variables from the .env file
load_dotenv()


# ChatOpenAI automatically reads OPENAI_API_KEY
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant who is good at recommending books."),
    MessagesPlaceholder(variable_name="messages")
])

chain = prompt | llm | StrOutputParser()

chat_history = InMemoryChatMessageHistory()


def chat(user_message: str) -> str:
    chat_history.add_messages([
        HumanMessage(content=user_message)
    ])

    response = chain.invoke({
        "messages": chat_history.messages
    })

    chat_history.add_messages([
        AIMessage(content=response)
    ])

    return response