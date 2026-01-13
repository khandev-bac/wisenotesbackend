import time

from .celery_app import celery_app


@celery_app.task(bind=True)
def example_task(self, content_id: str):
    for i in range(5):
        time.sleep(5)
        self.update_state(state="PROGRESS", meta={"percent": i * 20})
        print("running.........")

    return {"content_id": content_id, "status": "COMPLETED"}
