from typing import Any
from kafka import KafkaProducer
from loguru import logger

from common.utils import retry

from .protocols import MBProducer


def get_kafka_producer(servers: list[str], **kwargs: Any) -> KafkaProducer:
    def _inner() -> KafkaProducer:
        return KafkaProducer(bootstrap_servers=servers, **kwargs)

    logger.info('Connecting producer to kafka servers {}', servers)
    return retry(_inner, retries=5, interval=2)


def make_mb_producer(kafka_producer: KafkaProducer, topic: str, *, sync: bool = True) -> MBProducer:
    def _produce(key: str, value: str) -> None:
        kafka_producer.send(topic=topic, key=key.encode(), value=value.encode())
        if sync:
            kafka_producer.flush()

        logger.info('Produced message: (key={}, value={})', key, value)

    return _produce
