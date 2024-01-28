from fastapi import FastAPI
from database import connect_db, create_tables, disconnect_db
from passlib.context import CryptContext
from user_controller import router as user_router


app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app.include_router(user_router, prefix="/user", tags=["user"])
@app.on_event("startup")
async def startup_db():
    await connect_db()
    await create_tables()

@app.on_event("shutdown")
async def shutdown_db():
    await disconnect_db()

