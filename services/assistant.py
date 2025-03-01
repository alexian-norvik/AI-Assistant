from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from common import llms_constants
from config import OPENAI_API_KEY
from services import agent_tools

if not OPENAI_API_KEY:
    raise EnvironmentError("Setup OpenAI key as your environment variable")


def chatbot(query: str, language: str, name: str, chat_history: list) -> str:
    """
    Chat with the assistant
    :param query: User query
    :param language: User language
    :param name: Name of the company
    :param chat_history: History of conversation
    :return: Generated assistant response
    """
    llm = ChatOpenAI(
        model=llms_constants.OPENAI_MODEL,
        temperature=llms_constants.MODEL_TEMPERATURE,
        max_retries=llms_constants.MODEL_MAX_RETRIES,
        api_key=OPENAI_API_KEY,
    )
    tools = [agent_tools.house_search]
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", llms_constants.SYSTEM_PROMPT),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
            MessagesPlaceholder(variable_name="chat_history"),
        ]
    )

    agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    response = agent_executor.invoke({"language": language, "name": name, "input": query, "chat_history": chat_history})

    return response["output"]
