from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext


class User(BaseModel):
    name: str
    email: str
    password: str


class Tweet(BaseModel):
    text: str


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str


class Auth(BaseModel):
    hashed_user_id: str
    expiration_time: datetime


SECRET_KEY = "YOUR_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_hashed_password(password):
    return pwd_context.hash(password)


def create_access_token(hashed_user_id):
    expiration_time = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "hashed_user_id": hashed_user_id,
        "expiration_time": expiration_time
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_access_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    return payload


app = FastAPI()


@app.post("/login")
async def login(login_request: LoginRequest):
    user = await get_user_by_email(login_request.email) #get user from db
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not verify_password(login_request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    hashed_user_id = get_hashed_password(user.id)

    access_token = create_access_token(hashed_user_id)

    return LoginResponse(access_token=access_token, token_type="bearer")


@app.get("/tweets", dependencies=[Depends(get_current_user)])
async def get_tweets(current_user: Auth):
    # Get the tweets from the database
    tweets = []

    return tweets


async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)

    hashed_user_id = payload["hashed_user_id"]
    expiration_time = payload["expiration_time"]

    if datetime.utcnow() > expiration_time:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")

    return Auth(hashed_user_id=hashed_user_id, expiration_time=expiration_time)
