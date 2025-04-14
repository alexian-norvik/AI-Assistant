import json
import logging
from typing import Optional

from langchain.agents import AgentType, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
from langfuse.decorators import observe, langfuse_context
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory

import config
from common import constants, llms_constants
from config import langfuse
from services import agent_tools


@observe(as_type="translation")
async def translate_query(query: str) -> Optional[str]:
    """
    Translate user query to english
    :param query: last query of the user
    :return: translated query to English
    """
    try:
        system_prompt = langfuse.get_prompt(name="translator", label="latest")
        compiled_system_prompt = system_prompt.compile(armenian_transliteration=constants.ARMENIAN_TRANSLITERATION)
        translator = await config.ANTHROPIC_MODEL.messages.create(
            model=llms_constants.ANTHROPIC_MODEL,
            system=compiled_system_prompt.strip(),
            messages=[
                {"role": "user", "content": f"query: {query}"},
            ],
            temperature=llms_constants.TRANSLATION_TEMPERATURE,
            max_tokens=llms_constants.MODEL_MAX_TOKENS,
        )
        translated_query = json.loads(translator.content[0].text)

        langfuse_context.update_current_observation(
            input=query,
            model=llms_constants.ANTHROPIC_MODEL,
            usage_details={"input": translator.usage.input_tokens, "output": translator.usage.output_tokens},
        )

        return translated_query["english"]
    except Exception as e:
        logging.error(f"Failed to translate the query, error message: {e}", exc_info=True)


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
        logging.error(f"Failed to summarize the user query, error message: {e}")


async def gather_information(chat_history, gathered_info: dict):
    system_prompt = (
        llms_constants.INFORMATION_GATHERER_PROMPT.replace(
            "{cheatsheet}", json.dumps(constants.INFORMATION_GATHERING_FORMAT)
        )
        .replace("{gathered_info}", json.dumps(gathered_info))
        .replace("{sample}", json.dumps(constants.SAMPLE))
    )

    gatherer = await config.ANTHROPIC_MODEL.messages.create(
        model=llms_constants.ANTHROPIC_MODEL,
        temperature=0.0,
        system=system_prompt.strip(),
        messages=[{"role": "user", "content": f"Conversation history: {chat_history}"}],
        max_tokens=500,
    )

    gathered_info = json.loads(gatherer.content[0].text)

    return gathered_info


def rehydrate_message(msg_dict):
    msg_type = msg_dict.get("type")
    content = msg_dict.get("content")
    additional_kwargs = msg_dict.get("additional_kwargs", {})
    response_metadata = msg_dict.get("response_metadata", {})
    if msg_type == "human":
        return HumanMessage(content=content, additional_kwargs=additional_kwargs, response_metadata=response_metadata)
    elif msg_type == "ai":
        return AIMessage(content=content, additional_kwargs=additional_kwargs, response_metadata=response_metadata)
    elif msg_type == "system":
        return SystemMessage(content=content, additional_kwargs=additional_kwargs, response_metadata=response_metadata)
    else:
        raise ValueError(f"Got unsupported message type: {msg_dict}")


def rehydrate_memory(memory_dict):
    if isinstance(memory_dict, dict) and "chat_memory" in memory_dict:
        chat_mem = memory_dict["chat_memory"]
        if isinstance(chat_mem, dict) and "messages" in chat_mem:
            messages = chat_mem["messages"]
            rehydrated_messages = [rehydrate_message(m) if isinstance(m, dict) else m for m in messages]
            chat_mem["messages"] = rehydrated_messages
        memory_dict["chat_memory"] = ChatMessageHistory.model_validate(chat_mem)
    return ConversationBufferMemory.model_validate(memory_dict)


def chatbot(query, language, name, memory, gathered_info):
    llm = ChatAnthropic(
        model_name=llms_constants.ANTHROPIC_MODEL,
        api_key=config.ANTHROPIC_API_KEY,
        temperature=0.6,
        max_retries=3,
        timeout=None,
        stop=None,
    )
    tools = [agent_tools.house_search]

    system_prompt = config.langfuse.get_prompt(name="assistant_base_prompt", label="latest")
    memory = rehydrate_memory(memory)

    if isinstance(gathered_info, dict):
        gathered_info = json.dumps(gathered_info).replace("{", "{{").replace("}", "}}")

    compiled_system_prompt = system_prompt.compile(
        language=language,
        name=name,
        supported_languages=constants.SUPPORTING_LANGUAGES,
        armenian_transliteration=constants.ARMENIAN_TRANSLITERATION_STR,
        cheatsheet=constants.INFORMATION_GATHERING_FORMAT_STR,
        regions=constants.AVAILABLE_REGIONS_STR,
        sample=constants.SAMPLE_STR,
        gathered_info=gathered_info,
    )

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=True,
        memory=memory,
        agent_kwargs={"system_message": compiled_system_prompt},
        handle_parsing_errors=True,
    )

    response = agent.invoke(query)
    memory = memory.model_dump()

    return response["output"], memory
