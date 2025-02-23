from langchain_core.messages import HumanMessage

from assistant import app

config = {"configurable": {"thread_id": "conversation1"}}
language = "Armenian"

input_message = [HumanMessage(content="barev vonces?")]
output = app.invoke({"messages": input_message, "language": language}, config=config)
output["messages"][-1].pretty_print()
