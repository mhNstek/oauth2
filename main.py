from typing import Annotated
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

# This is a relative url, http://localhost:8000/token
# if the url changes to let's say http://localhost:8000/api,
# then the token url would be http://localhost:8000/api/token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/hello")
def hello_func():
    return "Hello World"


@app.get("/data")
def get_data():
    return {"data": "This is important data"}


@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}
