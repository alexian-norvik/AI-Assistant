import os
from typing import Sequence

from dotenv import load_dotenv
from langgraph.graph import START, StateGraph
from typing_extensions import Annotated, TypedDict
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage, trim_messages
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

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
        (
            "system",
            "You are an Helpful real estate company customer support assistant, that assists user to buy their dream home, and your name is Hoory. Assist the user in their own language: {language}",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

workflow = StateGraph(state_schema=State)


def call_model(state: State):
    trimmed_messages = trimmer.invoke(state["messages"])
    prompt = prompt_template.invoke({"messages": trimmed_messages, "language": state["language"]})
    response = model.invoke(prompt)
    return {"messages": response}


workflow.add_edge(START, "model")
workflow.add_node("model", call_model)


# add memory
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
