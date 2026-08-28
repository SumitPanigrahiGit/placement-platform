# Placement Platform API

A backend API for tracking job/internship postings and applications, built as part of my CSE portfolio project.

## Tech Stack
- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- JWT Authentication (python-jose)
- Password hashing (passlib/bcrypt)

## Features Built So Far
- User signup with hashed passwords
- User login with JWT token generation
- Protected routes requiring authentication
- Job postings: create and list
- Applications: apply to postings, view your own applications
- Relational database with foreign keys (Users, Job Postings, Applications)

## How to Run Locally
1. Install dependencies: `pip install fastapi uvicorn sqlalchemy psycopg2-binary passlib[bcrypt] python-jose[cryptography]`
2. Set up PostgreSQL and update the connection string in `database.py`
3. Run the server: `uvicorn main:app --reload`
4. Visit `http://127.0.0.1:8000/docs` to test all endpoints

## Coming Soon
- Automated data pipeline to fetch real job postings
- Deployment to cloud (Render/AWS)
- Docker containerization

## Live Demo
https://placement-platform-api.onrender.com/docs