from fastapi import FastAPI, Header
import uvicorn

app = FastAPI()

SECRET_KEY = "my_secret_key"


@app.post("/")
async def your_endpoint(authorization: str = Header(...)):
    # Now, authorization contains the value of the "Authorization" header
    return {"message": f"Hello, world! and {authorization}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
