from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from common import llms_constants
from config import ANTHROPIC_API_KEY
from services import agent_tools

if not ANTHROPIC_API_KEY:
    raise EnvironmentError("Setup Anthropic API key as your environment variable.")


def anthropic_chatbot(query: str, language: str, name: str, chat_history: list) -> str:
    llm = ChatAnthropic(
        model_name=llms_constants.ANTHROPIC_MODEL,
        temperature=llms_constants.MODEL_TEMPERATURE,
        max_retries=llms_constants.MODEL_MAX_RETRIES,
        api_key=ANTHROPIC_API_KEY,
        timeout=None,
        stop=None,
    )

    tools = [agent_tools.house_search]
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", llms_constants.CHATBOT_SYSTEM_PROMPT),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
            MessagesPlaceholder(variable_name="chat_history"),
        ]
    )

    agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    response = agent_executor.invoke({"language": language, "name": name, "input": query, "chat_history": chat_history})

    return response["output"][0]["text"]
