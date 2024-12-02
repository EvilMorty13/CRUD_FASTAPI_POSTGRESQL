from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()

celery_app = Celery(
    broker = os.getenv('REDIS_BROKER'),
    backend = os.getenv('REDIS_BACKEND')
)

@celery_app.task()
def send_email(subject: str, recipient: str, body: str):
    print("\n[Email Task]")
    print(f"To: {recipient}")
    print(f"Subject: {subject}")
    print(f"Body:\n{body}")
    return "Email sent (simulated)"



# celery_app.register_task(send_email)

