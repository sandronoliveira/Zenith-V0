"""
Serviço de Autenticação - Zenith V1
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# Configuração
SECRET_KEY = os.environ.get("JWT_SECRET", "your_jwt_secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Modelo de usuário
class User(BaseModel):
    id: int
    username: str
    password: str
    role: str
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str
    
    @classmethod
    def from_user(cls, user: User, hashed_password: str):
        return cls(
            id=user.id,
            username=user.username,
            password="",
            role=user.role,
            disabled=user.disabled,
            hashed_password=hashed_password
        )

class UserResponse(BaseModel):
    id: int
    username: str
    role: str

class Token(BaseModel):
    token: str
    user: UserResponse

# Banco de dados mock
fake_users_db = {
    "admin": {
        "id": 1,
        "username": "admin",
        "hashed_password": "$2b$12$yyCiw.3N0jOLuXoiTXZKHeX3.jzpzSO.CGwzOYoZxCDI8KrYIqNEO",  # "admin123"
        "role": "admin",
        "disabled": False
    },
    "user": {
        "id": 2,
        "username": "user",
        "hashed_password": "$2b$12$OGbLzz5DGU68LW9Qc3NfVOCmQzvQKnYNd6h5mYxXdTq00ZfOIW5Mm",  # "user123"
        "role": "user",
        "disabled": False
    }
}

# Segurança
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(title="Zenith Auth Service")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Funções de autenticação
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=username)
    if user is None:
        raise credentials_exception
    return user

# Rotas
@app.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "id": user.id, "role": user.role}, 
        expires_delta=access_token_expires
    )
    return {
        "token": access_token,
        "user": UserResponse(id=user.id, username=user.username, role=user.role)
    }

@app.get("/profile", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Usuário inativo")
    return UserResponse(id=current_user.id, username=current_user.username, role=current_user.role)

@app.get("/health")
async def health_check():
    return {"status": "ok"} 