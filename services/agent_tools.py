import json

from langchain_core.tools import tool


@tool
def house_search(gathered_info: str) -> dict:
    """
    Check if in the provided location there is any house for sale or not.
    :param gathered_info: gathered information from conversation with the client.
    :return: True or False whether any house is available or not.
    """
    gathered_info = json.loads(gathered_info)

    return gathered_info
