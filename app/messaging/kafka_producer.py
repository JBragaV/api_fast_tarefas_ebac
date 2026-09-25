import json

from aiokafka import AIOKafkaProducer

from app.core.configs import SysConfig

producer: AIOKafkaProducer | None = None


async def iniciar_producer():
    global producer
    producer = AIOKafkaProducer(
        bootstrap_servers=SysConfig.BOOTSTRAP_SERVER_KAFKA,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    await producer.start()


async def parar_producer():
    if producer:
        await producer.stop()


async def publicar_evento(topico: str, evento: dict):
    if producer:
        await producer.send_and_wait(topico, evento)
