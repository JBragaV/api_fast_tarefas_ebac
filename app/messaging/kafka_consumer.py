import asyncio
import json

from aiokafka import AIOKafkaConsumer

from app.core.configs import SysConfig


async def consumir():
    consumer = AIOKafkaConsumer(
        "usuario.criado",
        bootstrap_servers=SysConfig.BOOTSTRAP_SERVER_KAFKA,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        group_id="grupo-usuario-criado",
    )

    await consumer.start()
    try:
        async for msg in consumer:
            print(f"Evento Recebido {msg}")
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(consumir())


"""
Quer que eu explique antes a diferença conceitual entre Kafka e o Celery que você acabou de implementar (fila de tarefas vs. stream de eventos), para deixar claro por que os dois fazem sentido juntos no mesmo projeto? Sim, quero.
"""
