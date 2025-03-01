from langchain_core.tools import tool


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
