import uvicorn
import tiktoken
from loguru import logger
from fastapi import FastAPI, HTTPException

from common import schemas, llms_constants
from services import anthropic_assistant
from services.openai_assistant import openai_chatbot

app = FastAPI()


@app.post("/openai_chat", response_model=schemas.ChatResponse)
def openai_chat(request: schemas.ChatRequest):
    try:
        chat_history = [message.to_langchain() for message in request.chat_history]

        if len(chat_history) > 15:
            chat_history = chat_history[-15:]

        result = openai_chatbot(
            query=request.query, language=request.language, name=request.name, chat_history=chat_history
        )

        # update chat history
        conversation_history = request.chat_history.copy()
        conversation_history.append(schemas.Message(message_type=llms_constants.HUMAN_MSG, content=request.query))
        conversation_history.append(schemas.Message(message_type=llms_constants.AI_MSG, content=result))

        return schemas.ChatResponse(response=result, chat_history=conversation_history, language=request.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


@app.post("/anthropic_chat", response_model=schemas.ChatResponse)
async def anthropic_chat(request: schemas.ChatRequest):
    try:
        user_query = request.query
        chat_history = [message.to_langchain() for message in request.chat_history]

        if len(chat_history) > 15:
            chat_history = chat_history[-15:]

        query_encoding = tiktoken.get_encoding(llms_constants.TIKTOKEN_MODEL)
        tokens = query_encoding.encode(user_query)

        if len(tokens) > 30:
            user_query = anthropic_assistant.summarize_query(query=user_query)

        chat_response = await anthropic_assistant.anthropic_chatbot(
            query=user_query, language=request.language, name=request.name, chat_history=chat_history
        )

        # update chat history
        conversation_history = request.chat_history.copy()
        conversation_history.append(schemas.Message(message_type=llms_constants.HUMAN_MSG, content=user_query))
        conversation_history.append(schemas.Message(message_type=llms_constants.AI_MSG, content=chat_response))

        return schemas.ChatResponse(
            response=chat_response, chat_history=conversation_history, language=request.language
        )
    except Exception as e:
        logger.error(f"Failed to generate user response, error message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {e}")


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
