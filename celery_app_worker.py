from celery import Celery

celery_app = Celery(
    "blog_app",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery_app.conf.update(
    task_routes={
        "blog_app.tasks.send_email": {"queue": "email_queue"}
    }
)
