from kafka import KafkaProducer
from kafka.producer.future import FutureRecordMetadata
from loguru import logger

from .protocols import MBProducer


def make_mb_producer(kafka_producer: KafkaProducer, topic: str, *, sync: bool = True) -> MBProducer:
    def _produce(key: str, value: str) -> None:
        f: FutureRecordMetadata = kafka_producer.send(
            topic=topic,
            key=key.encode(),
            value=value.encode(),
        )
        if sync:
            f.get(timeout=10)

        logger.info('Produced message: (key={}, value={})', key, value)

    return _produce
