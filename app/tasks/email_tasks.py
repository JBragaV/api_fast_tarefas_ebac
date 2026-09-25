import logging

from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task
def task_envio_email_boas_vindas(nome: str, email: str):
    logger.info(f"Bem vindo, {nome}, enviei o email para {email}")
