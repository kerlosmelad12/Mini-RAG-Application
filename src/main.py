from fastapi import FastAPI
from routes import base
from dotenv import load_dotenv
load_dotenv('.env')
import uvicorn


app = FastAPI()
app.include_router(base.base_router)

if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, reload=True)