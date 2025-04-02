from typing import List

from pydantic import BaseModel
from langchain_core.messages import AIMessage, HumanMessage

from common import constants, llms_constants


class Message(BaseModel):
    message_type: str
    content: str

    def to_langchain(self):
        if self.message_type.lower() == llms_constants.HUMAN_MSG:
            return HumanMessage(content=self.content)
        elif self.message_type.lower() == llms_constants.AI_MSG:
            return AIMessage(content=self.content)

    @classmethod
    def from_langchain(cls, message):
        if isinstance(message, HumanMessage):
            return cls(message_type=llms_constants.HUMAN_MSG, content=message.content)
        elif isinstance(message, AIMessage):
            return cls(message_type=llms_constants.AI_MSG, content=message.content)


class ChatRequest(BaseModel):
    query: str
    language: str
    name: str
    chat_history: List[Message] = []
    information: dict = constants.information_gathering_format


class ChatResponse(BaseModel):
    response: str
    language: str
    chat_history: List[Message]
