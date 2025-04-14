import uvicorn
import tiktoken
from fastapi import FastAPI
from langchain.memory import ConversationBufferMemory

from common import schemas, llms_constants
from services import ai_assistant

app = FastAPI()


@app.post("/assistant", response_model=schemas.ChatResponse)
async def assistant(request: schemas.ChatRequest):
    user_query = request.query
    chat_history = request.chat_history

    if len(chat_history) > 15:
        chat_history = chat_history[-15:]

    query_encoding = tiktoken.get_encoding(llms_constants.TIKTOKEN_MODEL)
    tokens = query_encoding.encode(user_query)

    if len(tokens) > 30:
        user_query = ai_assistant.summarize_query(query=user_query)

    if not chat_history:
        chat_history = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    translated_query = await ai_assistant.translate_query(query=user_query)
    chat_response, chat_history = ai_assistant.chatbot(
        query=translated_query,
        language=request.language,
        name=request.name,
        memory=chat_history,
        gathered_info=request.gathered_info,
    )

    gathered_info = await ai_assistant.gather_information(
        chat_history=chat_history, gathered_info=request.gathered_info
    )

    return schemas.ChatResponse(
        response=chat_response, chat_history=chat_history, language=request.language, gathered_info=gathered_info
    )


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
