import config
from common import llms_constants

config.langfuse.create_prompt(
    name="assistant_base_prompt",
    type="text",
    prompt=llms_constants.CHATBOT_SYSTEM_PROMPT,
    labels=["latest"],
    config={
        "model": llms_constants.ANTHROPIC_MODEL,
        "temperature": 0.6,
        "supported_languages": ["hy"],
        "model_tools": ["house_search"],
    },
)

config.langfuse.create_prompt(
    name="translator",
    type="text",
    prompt=llms_constants.TRANSLATOR_SYSTEM_PROMPT,
    labels=["latest"],
    config={"model": llms_constants.ANTHROPIC_MODEL, "temperature": 0.0, "supported_languages": ["hy"]},
)
