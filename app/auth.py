from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from passlib.context import CryptContext
from app.db import User
from jose import jwt, JWTError

SECRET_KEY = "test908234Secret091Key"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="login")

def get_password_hash(password):
    return bcrypt_context.hash(password)

def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)

async def authenticate_user(email: str, password: str):
    user = await User.objects.get(email=email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def get_users(db: User, user_id: int):
    return db.objects.filter(User.id == user_id).first()

def create_access_token(username: str, user_id: int, expires_delta: timedelta = None):
    encode = {"sub": username, "id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: int = payload.get("id")
        if email is None or user_id is None:
            raise get_user_exception()
        user = User.objects.filter(email=email).filter(id=user_id).first()
        return await user
    except JWTError:
        raise get_user_exception()

def get_user_exception():
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return credentials_exception

def token_exception():
    token_exception_response = HTTPException(
        status_code=401,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"}
    )
    return token_exception_response
