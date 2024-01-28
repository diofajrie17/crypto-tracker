from fastapi import APIRouter, Depends, HTTPException, Header
from passlib.context import CryptContext
from datetime import timedelta
from coin import get_coin_data, get_rates_idr
from models import AuthResponse, Coin, CoinResponse, Token, User, UserResponse, UserSignIn, UserSignUp
from database import create_user, database, remove_coin, save_coin
from auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_user

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

@router.post("/signup", response_model=AuthResponse)
async def signup(user: UserSignUp):
    existing_user = await database.fetch_one("SELECT * FROM users WHERE email = :email", {"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    if user.password != user.password_confirmation:
        raise HTTPException(status_code=400, detail="Password and password confirmation do not match")

    hashed_password = pwd_context.hash(user.password)
    await create_user(UserSignIn(email=user.email, password=hashed_password))

    token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    return AuthResponse(email=user.email, token=token)

@router.post("/signin", response_model=AuthResponse)
async def signin(user: UserSignIn):
    existing_user = await database.fetch_one("SELECT * FROM users WHERE email = :email", {"email": user.email})
    if not existing_user or not pwd_context.verify(user.password, existing_user['password']):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    return AuthResponse(email=user.email, token=token)

@router.get("/me", response_model=UserSignIn)
async def read_users_me(current_user: UserSignIn = Depends(get_current_user)):
    return current_user

@router.post("/logout", response_model=Token)
async def logout(authorization: str = Header(..., convert_underscores=False), current_user: UserSignIn = Depends(get_current_user)):
    # just need to set the token to empty string
    return Token(access_token= "", token_type= "bearer")

@router.get("/coins", response_model=UserResponse)
async def get_tracked_coins(authorization: str = Header(..., convert_underscores=False), current_user: UserSignIn = Depends(get_current_user)):
    rate_idr = get_rates_idr()
    all_coin_data = get_coin_data()['data']

    tracked_coins = await database.fetch_all("SELECT * FROM coins WHERE user_id = :user_id", {"user_id": current_user.id})
    tracked_coin_data = [coin_data for coin_data in all_coin_data if coin_data['id'] in [coin['coin_id'] for coin in tracked_coins]]
    print(tracked_coin_data)
    coin_responses = [
        CoinResponse(
            id=coin['id'], 
            name=coin['name'], 
            price_in_rupiah=float(coin['priceUsd'])/float(rate_idr)
        ) for coin in tracked_coin_data]

    return UserResponse(coins=coin_responses)

@router.get("/coins/{id}", response_model=UserResponse)
async def get_tracked_coins(id: str,authorization: str = Header(..., convert_underscores=False), current_user: UserSignIn = Depends(get_current_user)):
    tracked_coins = await database.fetch_one(
        "SELECT * FROM coins WHERE user_id = :user_id AND coin_id = :coin_id", 
        {"user_id": current_user.id, "coin_id": id}
    )
    if not tracked_coins:
        raise HTTPException(status_code=400, detail=f"Coin with ID {id} has not been tracked")
    rate_idr = get_rates_idr()
    rate_usd_to_idr = float(rate_idr)
    coin_data = get_coin_data(tracked_coins['coin_id'])['data']
    price_in_rupiah = float(coin_data.get('priceUsd')) / rate_usd_to_idr
    coin_responses = [
        CoinResponse(name=tracked_coins['name'], price_in_rupiah=price_in_rupiah)]

    return UserResponse(coins=coin_responses)

@router.post("/addCoin/{id}")
async def get_tracked_coins(id: str,authorization: str = Header(..., convert_underscores=False), current_user: User = Depends(get_current_user)):
    coin_data = get_coin_data(id)['data']
    saved_coin = await database.fetch_one("SELECT * FROM coins WHERE user_id = :user_id AND coin_id = :coin_id", {"user_id":current_user.id ,"coin_id": id})
    if saved_coin:
        raise HTTPException(status_code=400, detail="Coin already saved")
    
    await save_coin(Coin(coin_id=coin_data['id'], name=coin_data['name'], user_id=current_user.id))

    return f"Coin with ID {id} has been successfully saved."

@router.post("/removeCoin/{id}")
async def get_tracked_coins(id: str,authorization: str = Header(..., convert_underscores=False), current_user: User = Depends(get_current_user)):
    saved_coin = await database.fetch_one("SELECT * FROM coins WHERE user_id = :user_id AND coin_id = :coin_id", {"user_id":current_user.id ,"coin_id": id})
    if not saved_coin:
        raise HTTPException(status_code=400, detail="Coin not found")
    
    await remove_coin(Coin(coin_id=saved_coin['coin_id'], name=saved_coin['name'], user_id=current_user.id))

    return f"Coin with ID {id} has been successfully removed."