from faststream.rabbit import RabbitQueue, RabbitExchange, ExchangeType
from faststream.rabbit.fastapi import RabbitRouter, RabbitBroker

rabbit_router = RabbitRouter("amqp://rabbitmq:5672/")
rabbit_broker = rabbit_router.broker

async def declare_queues(broker: RabbitBroker):
    await broker.declare_exchange(
        RabbitExchange("payments_exchange", type=ExchangeType.TOPIC, durable=True)
    )

    await broker.declare_queue(
        RabbitQueue("payments_queue", durable=True, routing_key="payments.new")
    )

    await broker.declare_queue(
        RabbitQueue("payments_dlq", durable=True, routing_key="payments.dlq")
    )
