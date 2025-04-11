import json
from typing import Optional

from loguru import logger
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_anthropic import ChatAnthropic
from langfuse.decorators import observe, langfuse_context
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

import config
from common import constants, llms_constants
from services import agent_tools

if not config.ANTHROPIC_API_KEY:
    raise EnvironmentError("Setup Anthropic API key as your environment variable.")


@observe(as_type="translation")
async def translate_query(query: str, language_code: str) -> Optional[str]:
    """
    Translate user query to english
    :param query: last query of the user
    :param language_code: language code of the conversation
    :return: translated query to English
    """
    try:
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

        langfuse_context.update_current_observation(
            input=query,
            model=llms_constants.ANTHROPIC_MODEL,
            usage_details={"input": translator.usage.input_tokens, "output": translator.usage.output_tokens},
        )

        return translated_query
    except Exception as e:
        logger.error(f"Failed to translate the query, error message: {e}")


@observe(as_type="summarizer")
async def summarize_query(query: str) -> Optional[str]:
    """
    Summarizes user query that exceeds the 10 token limit.
    :param query: user last query in the conversation.
    :return: summarized query
    """
    try:
        summarizer = await config.ANTHROPIC_MODEL.messages.create(
            model=llms_constants.ANTHROPIC_MODEL,
            system=llms_constants.CONVERSATION_SUMMARIZER_PROMPT,
            messages=[{"role": "user", "content": f"query: {query}"}],
            temperature=llms_constants.TRANSLATION_TEMPERATURE,
        )

        summarized_query = summarizer.content[0].text

        langfuse_context.update_current_observation(
            input=query,
            model=llms_constants.ANTHROPIC_MODEL,
            usage_details={"input": summarizer.usage.input_tokens, "output": summarizer.usage.output_tokens},
        )

        return summarized_query
    except Exception as e:
        logger.error(f"Failed to summarize the user query, error message: {e}")


@observe(as_type="assistant")
async def anthropic_chatbot(query: str, language: str, name: str, chat_history: list) -> Optional[str]:
    """
    chatbot for conversation with the user, to gather the necessary data in order to search for the best house.
    :param query: user last query
    :param language: language code of the conversation
    :param name: name of the agent.
    :param chat_history: conversation history
    :return: generated AI response.
    """
    try:
        llm = ChatAnthropic(
            model_name=llms_constants.ANTHROPIC_MODEL,
            temperature=llms_constants.MODEL_TEMPERATURE,
            max_retries=llms_constants.MODEL_MAX_RETRIES,
            api_key=config.ANTHROPIC_API_KEY,
            timeout=None,
            stop=None,
        )

        english_query = await translate_query(query=query, language_code=language)

        tools = [agent_tools.house_search]
        prompt = ChatPromptTemplate(
            [
                ("system", llms_constants.CHATBOT_SYSTEM_PROMPT),
                ("assistant", json.dumps(constants.INFORMATION_GATHERING_FORMAT).replace("{", "{{").replace("}", "}}")),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
                MessagesPlaceholder(variable_name="chat_history"),
            ]
        )

        agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

        response = await agent_executor.ainvoke(
            {"language": language, "name": name, "input": english_query, "chat_history": chat_history}
        )

        return response["output"][0]["text"]
    except Exception as e:
        logger.error(f"Failed to continue the conversation with the user, error message: {e}")
