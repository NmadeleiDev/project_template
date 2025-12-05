from domain.celery_app import celery_app


@celery_app.task
def test_task():
    print("Test task")
