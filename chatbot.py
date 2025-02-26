import os
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain.tools import tool
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage

import llms_constants

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise EnvironmentError("Setup the OpenAI API key as your environment variable.")


@tool
def house_search(location: str) -> bool:
    """
    Check if in the provided location there is any house for sale or not.
    :param location: Provided location by the user.
    :return: True or False whether any house is available or not.
    """
    if location in ["Yerevan", "Gyumri", "Spitak"]:
        return True
    else:
        return False


class Message(BaseModel):
    type: str
    content: str

    def to_langchain(self):
        if self.type == "human":
            return HumanMessage(content=self.content)
        elif self.type == "ai":
            return AIMessage(content=self.content)
        raise ValueError("Invalid message type")

    @classmethod
    def from_langchain(cls, message):
        if isinstance(message, HumanMessage):
            return cls(type="human", content=message.content)
        elif isinstance(message, AIMessage):
            return cls(type="ai", content=message.content)
        raise ValueError("Unsupported message type")


class ChatRequest(BaseModel):
    user_input: str
    language: str
    chat_history: List[Message] = []


class ChatResponse(BaseModel):
    response: str
    update_chat_history: List[Message]


app = FastAPI()

llm = ChatOpenAI(model="gpt-4o", temperature=0.3, max_retries=3)

tools = [house_search]

prompt = ChatPromptTemplate(
    [
        ("system", llms_constants.chatbot_system_prompt.strip()),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "client language: {language}\n{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

agent = create_openai_tools_agent(llm=llm, tools=tools, prompt=prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        chat_history = [msg.to_langchain() for msg in request.chat_history]

        result = agent_executor.invoke(
            {"input": request.user_input, "language": request.language, "chat_history": chat_history}
        )

        # Update chat history with new messages
        updated_history = request.chat_history.copy()
        updated_history.append(Message(type="human", content=request.user_input))
        updated_history.append(Message(type="ai", content=result["output"]))

        return ChatResponse(response=result["output"], update_chat_history=updated_history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
