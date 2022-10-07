from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

accept_all = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=accept_all,
    allow_credentials=True,
    allow_methods=accept_all,
    allow_headers=accept_all,
)


@app.get("/")
def read_root():
    return {"Welocme to": "Trips microservice"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
