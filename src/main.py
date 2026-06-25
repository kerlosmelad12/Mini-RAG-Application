from fastapi import FastAPI
from routes import base, data
import uvicorn


app = FastAPI()
app.include_router(base.base_router)
app.include_router(data.data_router)

if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, reload=True)