from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    skills: str = ""

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class JobPostingCreate(BaseModel):
    company_name: str
    role_title: str
    required_skills: str = ""
    source_url: str = ""

class JobPostingOut(JobPostingCreate):
    id: int

    class Config:
        from_attributes = True