from kafka import KafkaProducer
from loguru import logger

from .protocols import MBProducer


def make_mb_producer(kafka_producer: KafkaProducer, topic: str, *, sync: bool = True) -> MBProducer:
    def _produce(key: str, value: str) -> None:
        kafka_producer.send(topic=topic, key=key.encode(), value=value.encode())
        if sync:
            kafka_producer.flush()

        logger.info('Produced message: (key={}, value={})', key, value)

    return _produce
