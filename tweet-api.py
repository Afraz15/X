from fastapi import FastAPI, Body, Depends, Header, Request
from pydantic import BaseModel, Field
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
from datetime import datetime, timedelta
import passlib.hash
# import requests
import http
import jwt
import uvicorn


class User(BaseModel):
    name: str
    email: str
    password: str


class Login(BaseModel):
    email: str
    password: str


class getUser(BaseModel):
    id: int


class Tweet(BaseModel):
    # user_id: int = Field(..., ref="users")
    # client_jwt: str
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


def generate_jwt(user_id: str) -> str:
    payload = {
        'user_id': user_id,
        'expires': (datetime.utcnow() + timedelta(minutes=60)).isoformat(),
        'issued': (datetime.utcnow()).isoformat()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


# def check_if_hash(password: str, hashed)

# make an object as user class
def get_current_user(jwt_token: str):
    try:
        jwt_token = (jwt_token.split("Bearer")[1]).replace(" ", "")

        jwt_payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=["HS256"])
        client_id = jwt_payload["user_id"]
        # print(client_id)
        return (client_id)
    except jwt.ExpiredSignatureError:
        {"message": "Signature has expired"}
    except jwt.InvalidTokenError:
        {"message": "Signature Invalid expired"}
    ''' 

    '''
    # user = get_user(user_id)
    # if user is None:
    #     raise http.HTTPException(status_code=401, detail="Invalid token")


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


@app.post("/user/login")
async def login(client_data: Login = Body(...), db: MongoClient = Depends(get_database)):
    # try:
    EmailUserFromDB = db['users'].find_one({"email": client_data.email})
    # user_payload
    # print(generate_jwt(str(EmailUserFromDB['_id'])))

    match EmailUserFromDB:
        case None:
            return {"message": f"user with this email: {client_data['email']} does dot exist"}
        case _:
            # print('in _ case')
            match ("password" in EmailUserFromDB['password']):
                case True:
                    user_payload = generate_jwt(
                        str(EmailUserFromDB['_id']))
                    # print()
                    print(user_payload)
                case False:
                    decode_hash = passlib.hash.bcrypt.verify(
                        client_data.password, EmailUserFromDB['password'])
                    print(f"hash password: {decode_hash}")
                    match decode_hash:
                        case True:
                            user_payload = generate_jwt(
                                str(EmailUserFromDB['_id']))
                            print(jwt.decode(user_payload,
                                  SECRET_KEY, algorithms='HS256'))
                            return user_payload
                        case False:
                            return {"message": f"{EmailUserFromDB['email']} and password are not correct"}
'''
    '''

# userExistPassword = passlib.hash.bcrypt.verify(
#     client_data['password'], EmailUserFromDB["password"])
# userData = [EmailUserFromDB, userExistPassword]

# match bool(userData[EmailUserFromDB]['email']) and userData[userExistPassword]:
#     case True:
#         generate_jwt(EmailUserFromDB["_id"])
#     case False:
#         return {"message": f"user with this email: {client_data['email']} does dot exist"}
# # except:
# return {"message": f"{EmailUserFromDB['email']} and password are not correct"}

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
# async def create_tweet(tweet: Tweet = Body(...), authorization: str = Header("authentication")):
async def create_tweet(tweet: Tweet = Body(...), authorization: str = Header("authentication"), db: MongoClient = Depends(get_database)):
    # async def create_tweet(tweet: Tweet = Body(...)):
    client_jwt = get_current_user(authorization)
    tweet_data = tweet.model_dump()
    tweet_data['user_id'] = client_jwt
    tweet_data['createdAt'] = datetime.utcnow()
    inserted_tweet = db['tweets'].insert_one(tweet_data)

    return tweet

    # print(authorization)

    # print(authorization)
    # payload = jwt.decode(tweet_data.client_jwt,
    #                      SECRET_KEY, algorithms=["HS256"])
    # return {"message": f"the payload is {tweet_data['client_jwt']}"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


# @app.get("/users/{user_id}")
# async def get_user(user_id: int, db: MongoClient = Depends(get_database)):
#     user = await db['users'].find_one({'_id': user_id})
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user
