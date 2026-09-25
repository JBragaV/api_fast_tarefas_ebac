import pkgutil

from celery import Celery

from app import tasks as TaskDir
from app.core.configs import SysConfig

include = [
    f"app.tasks.{nome_modulo}"
    for _, nome_modulo, _ in pkgutil.iter_modules(TaskDir.__path__)
]
print(include)
celery_app = Celery(
    "app",
    broker=SysConfig.CELETY_BROKER,
    backend=SysConfig.CELETY_BACKEND,
    include=include,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="America/Sao_Paulo",
    enable_utc=True,
)

celery_app.autodiscover_tasks(["app"])
