import uvicorn

from chatbot import app

uvicorn.run(app, host="0.0.0.0", port=4000)
