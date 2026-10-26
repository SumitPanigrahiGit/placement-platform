from fastapi import FastAPI, Depends, HTTPException, Request, Query
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.staticfiles import StaticFiles
from sqlalchemy import or_
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from auth import create_access_token, get_current_user
from typing import List
from pipeline import fetch_and_store_jobs, start_scheduler

from database import engine, Base, get_db
import models
import schemas

app = FastAPI()

# Rate limiting: slows down password guessing and abuse (per client IP)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

start_scheduler()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.get("/")
def home():
    return {"message": "Placement Platform API is live"}

@app.get("/status")
def status():
    return {"day": 5, "status": "Signup endpoint ready"}

@app.post("/signup")
@limiter.limit("10/minute")
def signup(request: Request, user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = pwd_context.hash(user.password)

    new_user = models.User(
        name=user.name,
        email=user.email,
        password_hash=hashed_pw,
        skills=user.skills
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"id": new_user.id, "name": new_user.name, "email": new_user.email}

@app.post("/login")
@limiter.limit("5/minute")
def login(request: Request, user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()

    if not db_user or not pwd_context.verify(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(data={"sub": db_user.email, "user_id": db_user.id})

    return {"access_token": token, "token_type": "bearer"}

@app.get("/me")
def get_my_profile(current_user: dict = Depends(get_current_user)):
    return {"logged_in_as": current_user["email"], "user_id": current_user["user_id"]}

from typing import List

@app.post("/postings", response_model=schemas.JobPostingOut)
def create_posting(posting: schemas.JobPostingCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    new_posting = models.JobPosting(
        company_name=posting.company_name,
        role_title=posting.role_title,
        required_skills=posting.required_skills,
        source_url=posting.source_url
    )
    db.add(new_posting)
    db.commit()
    db.refresh(new_posting)
    return new_posting

def _like(text: str) -> str:
    """Escape % and _ so user input is matched literally, then wrap for a contains-search."""
    safe = text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{safe}%"

@app.get("/postings", response_model=List[schemas.JobPostingOut])
def list_postings(
    q: str = Query("", max_length=100, description="search in role title or company"),
    skill: str = Query("", max_length=50, description="filter by a required skill"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(models.JobPosting)
    if q:
        like = _like(q)
        query = query.filter(or_(
            models.JobPosting.role_title.ilike(like, escape="\\"),
            models.JobPosting.company_name.ilike(like, escape="\\"),
        ))
    if skill:
        query = query.filter(models.JobPosting.required_skills.ilike(_like(skill), escape="\\"))
    return query.order_by(models.JobPosting.id.desc()).offset(offset).limit(limit).all()

@app.post("/applications", response_model=schemas.ApplicationOut)
def apply_to_posting(application: schemas.ApplicationCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    posting = db.query(models.JobPosting).filter(models.JobPosting.id == application.posting_id).first()
    if not posting:
        raise HTTPException(status_code=404, detail="Job posting not found")

    new_application = models.Application(
        user_id=current_user["user_id"],
        posting_id=application.posting_id
    )
    db.add(new_application)
    db.commit()
    db.refresh(new_application)
    return new_application

@app.get("/applications/me", response_model=List[schemas.ApplicationOut])
def my_applications(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return db.query(models.Application).filter(models.Application.user_id == current_user["user_id"]).all()

@app.post("/pipeline/run-now")
@limiter.limit("2/minute")
def run_pipeline_now(request: Request, current_user: dict = Depends(get_current_user)):
    fetch_and_store_jobs()
    return {"message": "Pipeline triggered manually"}

app.mount("/app", StaticFiles(directory="static", html=True), name="static")