from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from common import llms_constants
from config import OPENAI_API_KEY

if not OPENAI_API_KEY:
    raise EnvironmentError("Setup OpenAI key as your environment variable")


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

    prompt = ChatPromptTemplate.from_messages([("system", llms_constants.SYSTEM_PROMPT), ("user", "{input}")])

    chain = prompt | llm

    response = chain.invoke({"language": language, "name": name, "input": query}).content

    return response
