from fastapi import FastAPI, Body, Depends, Header
from pydantic import BaseModel, Field
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
from datetime import datetime
import passlib.hash
# import requests
import http
import jwt
import uvicorn


class User(BaseModel):
    name: str
    email: str
    password: str


class getUser(BaseModel):
    id: int


class Tweet(BaseModel):
    # user_id: int = Field(..., ref="users")
    text: str
    # created_at: datetime


app = FastAPI()

uri = "mongodb+srv://tweet:tweet@tweet-api.jfdpjg3.mongodb.net/?retryWrites=true&w=majority"
SECRET_KEY = 'John-5'

tweetUser = ''


def get_database():
    # Create a new client and connect to the server
    dummy_client = MongoClient(uri, server_api=ServerApi('1'))
    # Get the database
    db = dummy_client['dummy_db']

    if dummy_client.server_info():
        print("Connected to MongoDB server")
        return db
    else:
        print("Connection to MongoDB server failed")
        return None


def generate_jwt(user_id: int) -> str:
    payload = {
        'user_id': user_id,
        'expires': datetime.utcnow() + timedelta(minutes=60),
        'issued': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


# make an object as user class
def get_current_user(client_jwt_token: str = Depends(Header("Authorization"))) -> User:
    try:
        payload = jwt.decode(client_jwt_token, SECRET_KEY,
                             algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise http.HTTPException(
            status_code=401, detail="Signature has expired")
    except jwt.InvalidTokenError:
        raise http.HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("user_id")
    if user_id is None:
        raise http.HTTPException(status_code=401, detail="Invalid token")
    user = get_user(user_id)
    if user is None:
        raise http.HTTPException(status_code=401, detail="Invalid token")
    return user


@app.get('/')
async def home():
    return {"message": "Hello Tweet API"}


@app.get("/users")
async def get_users(db: MongoClient = Depends(get_database)):
    users = db['users'].find()
    modified_users = []
    for i in users:
        i['_id'] = str(i['_id'])
        modified_users.append(i)

        print(i)
    return modified_users[4]["password"]
    # return passlib.hash.bcrypt.verify("john5", modified_users[4]["password"])
    # return True

""""
password not hashed

@app.post("/users")
async def create_user(user: User = Body(...), db: MongoClient = Depends(get_database)):
    inserted_user = db['users'].insert_one(user.model_dump(by_alias=True))
    return {"message": f"User created with ID: {inserted_user.inserted_id}"}
"""


@app.post("/users")
async def create_user(user: User = Body(...), db: MongoClient = Depends(get_database)):
    user_data = user.model_dump(by_alias=True)
    user_data['password'] = passlib.hash.bcrypt.hash(user_data['password'])
    inserted_user = db['users'].insert_one(user_data)
    return {"message": f"User created with ID: {inserted_user.inserted_id}"}


@app.get("/get_user")
def get_user(user_name: str, db: MongoClient = Depends(get_database)):
    id = ObjectId(user_name)
    user = db['users'].find_one({"_id": id})
    # user['_id'] = str(user['_id'])
    # tweetUser = user['id']   # password      # was getting error for id was in some alien format for json
    print(user)
    # return user


@app.get("/tweets")
async def get_tweets(db: MongoClient = Depends(get_database)):
    tweets = db['tweets'].find()
    modified_tweets = []
    for i in tweets:
        i['_id'] = str(i['_id'])
        modified_tweets.append(i)
    return modified_tweets


@app.post("/tweets")
async def create_tweet(tweet: Tweet = Body(...), db: MongoClient = Depends(get_database)):
    tweet_data = tweet.model_dump()
    tweet_data['user_id'] = tweetUser
    tweet_data['createdAt'] = datetime.now()
    inserted_tweet = db['tweets'].insert_one(tweet_data)
    return tweet


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


# @app.get("/users/{user_id}")
# async def get_user(user_id: int, db: MongoClient = Depends(get_database)):
#     user = await db['users'].find_one({'_id': user_id})
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user
