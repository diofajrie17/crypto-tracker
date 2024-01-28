from databases import Database

DATABASE_URL = "sqlite:///./test.db"

database = Database(DATABASE_URL)

async def create_tables():
    await database.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
        """
    )

    await database.execute(
        """
        CREATE TABLE IF NOT EXISTS coins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin_id TEXT NOT NULL,
            name TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
    )
    
async def connect_db():
    await database.connect()

async def disconnect_db():
    await database.disconnect()
    
async def create_user(user):
    query = "INSERT INTO users (email, password) VALUES (:email, :password)"
    values = {"email": user.email, "password": user.password}
    await database.execute(query, values)
    
async def save_coin(coin):
    query = "INSERT INTO coins (coin_id, name, user_id) VALUES (:coin_id, :name, :user_id)"
    values = {"coin_id": coin.coin_id, "name": coin.name, "user_id": coin.user_id}
    await database.execute(query, values)
    
async def remove_coin(coin):
    query = "DELETE FROM coins WHERE user_id = :user_id AND coin_id = :coin_id"
    values = {"user_id": coin.user_id, "coin_id": coin.coin_id}
    await database.execute(query, values)
