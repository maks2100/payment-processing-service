from faststream.rabbit import RabbitExchange, RabbitQueue
from faststream.rabbit.fastapi import RabbitRouter, RabbitBroker

from src.core.enums import RabbitQueuesEnum

router = RabbitRouter("amqp://rabbitmq:5672/")
broker = router.broker


def get_broker() -> RabbitBroker:
    return broker

PAYMENT_EXCHANGE = RabbitExchange("payments")

PAYMENT_DLQ_QUEUE = RabbitQueue(
    RabbitQueuesEnum.PAYMENT_DLQ,
    routing_key=RabbitQueuesEnum.PAYMENT_NEW,
    arguments={
        "x-dead-letter-exchange": "payments",
        "x-dead-letter-routing-key": RabbitQueuesEnum.PAYMENT_DLQ,
    },
)

PAYMENT_NEW_QUEUE = RabbitQueue(
    RabbitQueuesEnum.PAYMENT_NEW,
    durable=True,
    routing_key=RabbitQueuesEnum.PAYMENT_NEW,
    arguments={
        "x-dead-letter-exchange": PAYMENT_EXCHANGE.name,
        "x-dead-letter-routing-key": RabbitQueuesEnum.PAYMENT_DLQ,
    },
)

RABBIT_QUEUES = {
    RabbitQueuesEnum.PAYMENT_NEW.value: PAYMENT_NEW_QUEUE,
    RabbitQueuesEnum.PAYMENT_DLQ.value: PAYMENT_DLQ_QUEUE,
}

RABBIT_EXCHANGES = {
    RabbitQueuesEnum.PAYMENT_NEW.value: PAYMENT_EXCHANGE,
    RabbitQueuesEnum.PAYMENT_DLQ.value: PAYMENT_EXCHANGE,
}