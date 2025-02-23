from langchain_core.messages import HumanMessage

from assistant import app

config = {"configurable": {"thread_id": "conversation1"}}
language = "Armenian"

input_message = [
    HumanMessage(
        content="Hi I'm norvik, I want a house, my budget is 100,000. In Yerevan Armenia, around 100 square meter with 2 rooms"
    )
]
output = app.invoke({"messages": input_message, "language": language}, config=config)
output["messages"][-1].pretty_print()
