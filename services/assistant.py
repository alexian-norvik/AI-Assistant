from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from common import llms_constants
from config import OPENAI_API_KEY

if not OPENAI_API_KEY:
    raise EnvironmentError("Setup OpenAI key as your environment variable")


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


def chat(query: str, language: str, name: str) -> str:
    """
    Chat with the assistant
    :param query: User query
    :param language: User language
    :param name: Name of the company
    :return: Generated assistant response
    """
    llm = ChatOpenAI(
        model=llms_constants.OPENAI_MODEL,
        temperature=llms_constants.MODEL_TEMPERATURE,
        max_retries=llms_constants.MODEL_MAX_RETRIES,
        api_key=OPENAI_API_KEY,
    )
    tools = [house_search]
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", llms_constants.SYSTEM_PROMPT),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    response = agent_executor.invoke({"language": language, "name": name, "input": query})

    return response["output"]
