from datetime import timedelta
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from auth import create_token, authenticate_user, RoleChecker, get_current_active_user, validate_refresh_token, oauth2_scheme
from data import fake_user_db, refresh_tokens
from models import User, Token

app = FastAPI()

ACCESS_TOKEN_EXPIRE_MINUTES = 20
REFRESH_TOKEN_EXPIRE_MINUTES = 120


@app.get("/hello")
def hello_func():
    return "Hello World"


@app.get("/data")
def get_data():
    return {"data": "This is important data"}


@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}


@app.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate_user(fake_user_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    access_token = create_token(data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires)
    refresh_token = create_token(data={"sub": user.username, "role": user.role}, expires_delta=refresh_token_expires)
    refresh_tokens.append(refresh_token)
    return Token(access_token=access_token, refresh_token=refresh_token)


@app.post("/refresh")
async def refresh_access_token(token_data: Annotated[tuple[User, str], Depends(validate_refresh_token)]):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    user, token = token_data
    access_token = create_token(data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires)
    refresh_token = create_token(data={"sub": user.username, "role": user.role}, expires_delta=refresh_token_expires)

    refresh_tokens.remove(token)
    refresh_tokens.append(refresh_token)
    return Token(access_token=access_token, refresh_token=refresh_token)


@app.get("/data")
def get_data(_: Annotated[bool, Depends(RoleChecker(allowed_roles=["admin"]))]):
    return {"data": "This is important data"}
