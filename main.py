from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Placement Platform API is live"}

@app.get("/status")
def status():
    return {"day": 3, "status": "API running successfully"}