import requests
from apscheduler.schedulers.background import BackgroundScheduler
from database import SessionLocal
import models

def fetch_and_store_jobs():
    print("Pipeline running: fetching jobs...")
    db = SessionLocal()
    try:
        response = requests.get("https://remotive.com/api/remote-jobs?limit=10")
        data = response.json()
        jobs = data.get("jobs", [])

        new_count = 0
        for job in jobs:
            existing = db.query(models.JobPosting).filter(
                models.JobPosting.source_url == job.get("url")
            ).first()

            if not existing:
                new_posting = models.JobPosting(
                    company_name=job.get("company_name", "Unknown"),
                    role_title=job.get("title", "Unknown Role"),
                    required_skills=job.get("tags", ""),
                    source_url=job.get("url", "")
                )
                db.add(new_posting)
                new_count += 1

        db.commit()
        print(f"Pipeline finished: {new_count} new postings added.")
    except Exception as e:
        print(f"Pipeline error: {e}")
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_and_store_jobs, "interval", hours=6)
    scheduler.start()