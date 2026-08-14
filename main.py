from fastapi import FastAPI
from database import engine, Base
import models

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message": "Placement Platform API is live"}

@app.get("/status")
def status():
    return {"day": 4, "status": "Connected to PostgreSQL"}