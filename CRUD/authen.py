from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from service.jwttoken import create_access_token
from service.oauth import get_current_user
from service.hashing import Hash
from database import conn
from schemas import User, UserResponse
from models import Users

from cryptography.fernet import Fernet

import dotenv, os

dotenv.load_dotenv()
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

cipher_suite = Fernet(ENCRYPTION_KEY)

auth = APIRouter()

def encrypt_email(email: str) -> str:
    return cipher_suite.encrypt(email.encode()).decode()

def decrypt_email(encrypted_email: str) -> str:
    return cipher_suite.decrypt(encrypted_email.encode()).decode()

def decrypt_user_data(user: dict) -> dict:
    if "email" in user and user["email"]:
        try:
            user["email"] = decrypt_email(user["email"])
        except Exception:
            user["email"] = "decryption_error"
    return user

def superuser_required(current_user: User = Depends(get_current_user)):
    # This function ensures that only superusers can access the endpoint.
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action"
        )
    return current_user

@auth.get("/users", response_model=list[UserResponse])
async def retrieve_all_user(current_user: User = Depends(get_current_user)):
    # If you want to restrict this endpoint as well, include superuser_required.
    users = conn.execute(Users.select()).fetchall()
    return [decrypt_user_data(dict(user._mapping)) for user in users]

@auth.get("/user/{id}", response_model=UserResponse)
async def retrieve_one_user(id: int, current_user: User = Depends(superuser_required)):
    user = conn.execute(Users.select().where(Users.c.id == id)).fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return decrypt_user_data(dict(user._mapping))

@auth.patch("/user/{id}", response_model=list[UserResponse])
async def update_user_data(id: int, req: User, current_user: User = Depends(superuser_required)):
    conn.execute(
        Users.update().values(
            username=req.username,
            email=encrypt_email(req.email),
        ).where(Users.c.id == id)
    )
    users = conn.execute(Users.select()).fetchall()
    return [decrypt_user_data(dict(user._mapping)) for user in users]

@auth.delete("/user/{id}", response_model=list[UserResponse])
async def delete_user_data(id: int, current_user: User = Depends(superuser_required)):
    conn.execute(Users.delete().where(Users.c.id == id))
    users = conn.execute(Users.select()).fetchall()
    return [decrypt_user_data(dict(user._mapping)) for user in users]

@auth.post('/register', response_model=list[UserResponse])
def create_user(req: User):
    conn.execute(
        Users.insert().values(
            username=req.username,
            email=encrypt_email(req.email),
            is_superuser=req.is_superuser,
            password=Hash.bcrypt(req.password)
        )
    )
    users = conn.execute(Users.select()).fetchall()
    return [decrypt_user_data(dict(user._mapping)) for user in users]

@auth.post('/login')
def login(req: OAuth2PasswordRequestForm = Depends()):
    user = conn.execute(Users.select().where(Users.c.username == req.username)).fetchone()
    if not user:
        raise HTTPException(status_code=404, detail=f"No user found with the username {req.username}")
    if not Hash.verify(user[-1], req.password):
        raise HTTPException(status_code=401, detail="Wrong username or password")
    decrypted_email = decrypt_email(user[2])
    access_token = create_access_token(
        data={"username": user[1], "email": decrypted_email, "is_superuser": user[3]}
    )
    return {"access_token": access_token, "token_type": "bearer", "id": user[0]}

@auth.get("/verify_token")
def read_root(current_user: User = Depends(get_current_user)):
    return current_user

@auth.patch("/change_superuser/{id}", response_model=list[UserResponse])
def change_superuser(id: int, req: User, current_user: User = Depends(superuser_required)):
    if req.is_superuser:
        conn.execute(Users.update().values(is_superuser=False).where(Users.c.id == id))
    else:
        conn.execute(Users.update().values(is_superuser=True).where(Users.c.id == id))
    users = conn.execute(Users.select()).fetchall()
    return [decrypt_user_data(dict(user._mapping)) for user in users]
