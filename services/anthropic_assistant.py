import json

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

import config
from common import llms_constants
from services import agent_tools

if not config.ANTHROPIC_API_KEY:
    raise EnvironmentError("Setup Anthropic API key as your environment variable.")


async def translate_query(query: str, language_code: str) -> str:
    """
    Translate user query to english
    :param query: last query of the user
    :param language_code: language code of the conversation
    :return: translated query to English
    """
    system_prompt = llms_constants.TRANSLATOR_SYSTEM_PROMPT.replace("{language_code}", language_code)

    translator = await config.ANTHROPIC_MODEL.messages.create(
        model=llms_constants.ANTHROPIC_MODEL,
        system=system_prompt,
        messages=[
            {"role": "user", "content": f"query: {query}"},
        ],
        temperature=llms_constants.TRANSLATION_TEMPERATURE,
        max_tokens=llms_constants.MODEL_MAX_TOKENS,
    )
    translated_query = json.loads(translator.content[0].text)["translated_query"]

    return translated_query


async def anthropic_chatbot(query: str, language: str, name: str, chat_history: list) -> str:
    """
    chatbot for conversation with the user, to gather the necessary data in order to search for the best house.
    :param query: user last query
    :param language: language code of the conversation
    :param name: name of the agent.
    :param chat_history: conversation history
    :return: generated AI response.
    """
    llm = ChatAnthropic(
        model_name=llms_constants.ANTHROPIC_MODEL,
        temperature=llms_constants.MODEL_TEMPERATURE,
        max_retries=llms_constants.MODEL_MAX_RETRIES,
        api_key=config.ANTHROPIC_API_KEY,
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

    response = await agent_executor.ainvoke(
        {"language": language, "name": name, "input": query, "chat_history": chat_history}
    )

    return response["output"][0]["text"]
