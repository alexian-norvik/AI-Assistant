import os
from typing import Optional, Sequence

from dotenv import load_dotenv
from langgraph.graph import START, StateGraph
from typing_extensions import Annotated, TypedDict
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage, trim_messages
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

import llms_constants

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

model = init_chat_model("gpt-4o", model_provider="openai")

trimmer = trim_messages(
    max_tokens=65, strategy="last", token_counter=model, include_system=True, allow_partial=False, start_on="human"
)


class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    language: str


prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", llms_constants.system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

workflow = StateGraph(state_schema=State)


@tool
def search_house(price: str, location: str, square_meter: str, rooms_amount: int, name: Optional[str]) -> str:
    """
    Search for the house in the database to suggest to the user that is looking for house
    :param price: exact or price range
    :param location: location of the house
    :param square_meter: square meter of the house
    :param rooms_amount: number of rooms
    :param name: name of the user
    :return: structured format of the information to call API
    """
    request_info = {
        "price": price,
        "location": location,
        "square_meter": square_meter,
        "rooms": rooms_amount,
        "name": name,
    }

    return f"this is your details: {request_info}"


model_with_tools = model.bind_tools([search_house])


def call_model(state: State):
    trimmed_messages = trimmer.invoke(state["messages"])
    prompt = prompt_template.invoke({"messages": trimmed_messages, "language": state["language"]})
    response = model_with_tools.invoke(prompt)
    return {"messages": response}


workflow.add_edge(START, "model")
workflow.add_node("model", call_model)


# add memory
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
