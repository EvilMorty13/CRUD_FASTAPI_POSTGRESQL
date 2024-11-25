from celery_app_worker import celery_app

@celery_app.task(name='blog_app.tasks.send_email')
def send_email(subject: str, recipient: str, body: str):
    print("\n[Email Task]")
    print(f"To: {recipient}")
    print(f"Subject: {subject}")
    print(f"Body:\n{body}\n")
    return "Email sent (simulated)"
