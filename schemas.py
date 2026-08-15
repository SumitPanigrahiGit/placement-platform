from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    skills: str = ""

class UserLogin(BaseModel):
    email: EmailStr
    password: str