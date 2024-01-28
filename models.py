from typing import List
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    id: int
    email: EmailStr
    password: str

class UserSignUp(BaseModel):
    email: EmailStr
    password: str
    password_confirmation: str
    
class UserSignIn(BaseModel):
    email: EmailStr
    password: str
    
class AuthResponse(BaseModel):
    email: EmailStr
    token: str
    
class Token(BaseModel):
    access_token: str
    token_type: str

class Coin(BaseModel):
    coin_id: str
    name: str
    user_id: int

class CoinResponse(BaseModel):
    name: str
    price_in_rupiah: float  

class UserResponse(BaseModel):
    coins: List[CoinResponse]  